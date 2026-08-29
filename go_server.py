"""Moltwork Go activation surface.

Run instead of server.py:
    uvicorn go_server:app --host 0.0.0.0 --port 8788

It imports the existing Moltwork marketplace app and adds the minimal activation
contract used by Moltbook, MoltOS, OpenClaw/Hermes AgentSkills, and generic HTTP
agents.

Security invariants:
- Moltbook permanent API keys are never accepted; only temporary identity tokens.
- MoltOS permanent API keys are never accepted.
- identity tokens/signatures are verified but never persisted.
- wallet signing material is never returned or persisted by Moltwork.
- new wallets are receive-first: outbound spending is disabled by policy.
- if CDP is not configured, activation reports wallet setup honestly instead of
  fabricating an address.
"""
from __future__ import annotations

import asyncio
import json
import os
import secrets
import time
import urllib.error
import urllib.request
import uuid
from typing import Any

from fastapi import Header, HTTPException
from pydantic import BaseModel

from server import app, create_worker, get_db, WorkerReq

MOLTBOOK_VERIFY_URL = "https://www.moltbook.com/api/v1/agents/verify-identity"
MOLTOS_PUBLIC_PROFILE = "https://moltos.org/api/agent/{agent_id}/public"
MOLTOS_VERIFY_SIGNATURE = "https://moltos.org/api/agent/pubkey"


class GoActivateReq(BaseModel):
    name: str = ""
    runtime: str = "generic"
    client_id: str = ""
    moltos_agent_id: str = ""
    moltos_challenge: str = ""
    moltos_signature: str = ""


class GoChallengeReq(BaseModel):
    provider: str
    external_id: str


def _init_go_tables() -> None:
    conn = get_db()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS go_identities (
            provider TEXT NOT NULL,
            external_id TEXT NOT NULL,
            worker_id TEXT NOT NULL,
            verified INTEGER NOT NULL DEFAULT 0,
            profile_json TEXT NOT NULL DEFAULT '{}',
            created_at REAL NOT NULL,
            PRIMARY KEY(provider, external_id)
        );
        CREATE TABLE IF NOT EXISTS go_wallets (
            worker_id TEXT PRIMARY KEY,
            provider TEXT NOT NULL,
            address TEXT NOT NULL DEFAULT '',
            network TEXT NOT NULL DEFAULT '',
            asset TEXT NOT NULL DEFAULT 'USDC',
            status TEXT NOT NULL,
            policy_json TEXT NOT NULL,
            created_at REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS go_sessions (
            id TEXT PRIMARY KEY,
            worker_id TEXT NOT NULL,
            runtime TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at REAL NOT NULL,
            updated_at REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS go_human_tasks (
            id TEXT PRIMARY KEY,
            worker_id TEXT NOT NULL,
            task_type TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            metadata_json TEXT NOT NULL DEFAULT '{}',
            created_at REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS go_challenges (
            provider TEXT NOT NULL,
            external_id TEXT NOT NULL,
            challenge TEXT NOT NULL,
            expires_at REAL NOT NULL,
            PRIMARY KEY(provider, external_id)
        );
        """
    )
    conn.commit()
    conn.close()


_init_go_tables()


def _json_request(url: str, *, method: str = "GET", headers: dict[str, str] | None = None,
                  body: dict[str, Any] | None = None, timeout: float = 10) -> dict[str, Any]:
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Accept", "application/json")
    if body is not None:
        req.add_header("Content-Type", "application/json")
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")[:500]
        raise ValueError(f"identity provider returned HTTP {exc.code}: {detail}") from exc
    except Exception as exc:
        raise ValueError(f"identity provider unavailable: {exc}") from exc


async def _verify_moltbook(token: str) -> dict[str, Any]:
    app_key = os.getenv("MOLTBOOK_APP_KEY", "").strip()
    if not app_key:
        raise HTTPException(503, "MOLTBOOK_APP_KEY is not configured on the Moltwork service")
    try:
        result = await asyncio.to_thread(
            _json_request,
            MOLTBOOK_VERIFY_URL,
            method="POST",
            headers={"X-Moltbook-App-Key": app_key},
            body={"token": token},
        )
    except ValueError as exc:
        raise HTTPException(401, str(exc)) from exc
    if not result.get("success") or not result.get("valid") or not result.get("agent"):
        raise HTTPException(401, "invalid or expired Moltbook identity token")
    return result["agent"]


async def _molt_os_public_profile(agent_id: str) -> dict[str, Any]:
    try:
        return await asyncio.to_thread(
            _json_request,
            MOLTOS_PUBLIC_PROFILE.format(agent_id=agent_id),
        )
    except ValueError as exc:
        raise HTTPException(401, str(exc)) from exc


def _consume_challenge(provider: str, external_id: str, message: str) -> bool:
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM go_challenges WHERE provider=? AND external_id=?",
        (provider, external_id),
    ).fetchone()
    if not row:
        conn.close()
        return False
    ok = row["challenge"] == message and row["expires_at"] >= time.time()
    if ok:
        conn.execute(
            "DELETE FROM go_challenges WHERE provider=? AND external_id=?",
            (provider, external_id),
        )
        conn.commit()
    conn.close()
    return ok


async def _verify_moltos_signature(agent_id: str, message: str, signature: str) -> bool:
    if not _consume_challenge("moltos", agent_id, message):
        return False
    try:
        result = await asyncio.to_thread(
            _json_request,
            MOLTOS_VERIFY_SIGNATURE,
            method="POST",
            body={"agent_id": agent_id, "message": message, "signature": signature},
        )
    except ValueError:
        return False
    return bool(result.get("valid") or result.get("verified") or result.get("success"))


def _find_identity(provider: str, external_id: str) -> dict[str, Any] | None:
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM go_identities WHERE provider=? AND external_id=?",
        (provider, external_id),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def _create_identity(provider: str, external_id: str, name: str, verified: bool,
                     profile: dict[str, Any]) -> str:
    existing = _find_identity(provider, external_id)
    if existing:
        return existing["worker_id"]

    worker = create_worker(WorkerReq(name=name, specialties=[], bio="Moltwork Go worker"))["worker"]
    conn = get_db()
    conn.execute(
        "INSERT INTO go_identities VALUES (?,?,?,?,?,?)",
        (provider, external_id, worker["id"], 1 if verified else 0,
         json.dumps(profile, separators=(",", ":")), time.time()),
    )
    conn.commit()
    conn.close()
    return worker["id"]


def _default_wallet_policy() -> dict[str, Any]:
    return {
        "receive_enabled": True,
        "spend_enabled": False,
        "max_per_transaction_usd": 0.0,
        "daily_spend_cap_usd": 0.0,
        "withdrawal_requires_human": True,
    }


async def _provision_wallet(worker_id: str) -> dict[str, Any]:
    conn = get_db()
    row = conn.execute("SELECT * FROM go_wallets WHERE worker_id=?", (worker_id,)).fetchone()
    conn.close()
    if row:
        wallet = dict(row)
        wallet["policy"] = json.loads(wallet.pop("policy_json"))
        return wallet

    policy = _default_wallet_policy()
    creds_present = all(
        os.getenv(k, "").strip()
        for k in ("CDP_API_KEY_ID", "CDP_API_KEY_SECRET", "CDP_WALLET_SECRET")
    )
    provider = "coinbase_cdp"
    address = ""
    network = "eip155:8453"  # Base mainnet; EOA address itself is EVM-portable.
    status = "operator_setup_required"

    if creds_present:
        try:
            from cdp import CdpClient  # provided by the cdp-sdk package
            async with CdpClient() as client:
                # Name makes recovery/idempotency clearer in the wallet provider.
                account = await client.evm.get_or_create_account(name=f"moltwork-{worker_id}")
                address = account.address
            status = "ready"
        except ImportError:
            status = "cdp_sdk_missing"
        except Exception:
            # Do not synthesize or guess an address if provisioning failed.
            status = "provisioning_failed"

    conn = get_db()
    conn.execute(
        "INSERT INTO go_wallets VALUES (?,?,?,?,?,?,?,?)",
        (worker_id, provider, address, network, "USDC", status,
         json.dumps(policy, separators=(",", ":")), time.time()),
    )
    conn.commit()
    conn.close()
    return {
        "worker_id": worker_id,
        "provider": provider,
        "address": address,
        "network": network,
        "asset": "USDC",
        "status": status,
        "policy": policy,
    }


def _get_or_create_safety_task(worker_id: str, wallet: dict[str, Any]) -> dict[str, Any]:
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM go_human_tasks WHERE worker_id=? AND task_type='wallet_safety' ORDER BY created_at DESC LIMIT 1",
        (worker_id,),
    ).fetchone()
    if row:
        conn.close()
        task = dict(row)
        task["metadata"] = json.loads(task.pop("metadata_json"))
        return task

    tid = f"ht-{uuid.uuid4().hex[:10]}"
    address_text = wallet.get("address") or "Wallet provisioning is not configured yet."
    description = (
        "This agent has a receive-first work wallet. It can receive verified earnings, but Moltwork "
        "will not authorize outbound wallet spending until you explicitly enable a non-zero limit. "
        "Withdrawals also require human approval. Never paste a seed phrase, private key, wallet "
        "secret, or another platform's permanent API key into Moltwork. "
        f"Wallet: {address_text}"
    )
    metadata = {
        "wallet_address": wallet.get("address", ""),
        "network": wallet.get("network", ""),
        "spend_enabled": False,
    }
    conn.execute(
        "INSERT INTO go_human_tasks VALUES (?,?,?,?,?,?,?,?)",
        (tid, worker_id, "wallet_safety", "Review your agent's work wallet", description,
         "pending", json.dumps(metadata, separators=(",", ":")), time.time()),
    )
    conn.commit()
    conn.close()
    return {
        "id": tid,
        "worker_id": worker_id,
        "task_type": "wallet_safety",
        "title": "Review your agent's work wallet",
        "description": description,
        "status": "pending",
        "metadata": metadata,
    }


@app.post("/api/go/challenge")
def go_challenge(req: GoChallengeReq):
    if req.provider != "moltos":
        raise HTTPException(400, "challenge flow currently supports provider=moltos")
    if not req.external_id:
        raise HTTPException(400, "external_id is required")
    message = f"moltwork-go:{secrets.token_urlsafe(32)}"
    expires_at = time.time() + 300
    conn = get_db()
    conn.execute(
        "INSERT OR REPLACE INTO go_challenges VALUES (?,?,?,?)",
        (req.provider, req.external_id, message, expires_at),
    )
    conn.commit()
    conn.close()
    return {"message": message, "expires_at": expires_at}


@app.post("/api/go/activate")
async def go_activate(
    req: GoActivateReq,
    x_moltbook_identity: str | None = Header(default=None, alias="X-Moltbook-Identity"),
):
    provider = "moltwork"
    external_id = f"native:{uuid.uuid4().hex}"
    profile: dict[str, Any] = {}
    verified = False
    name = req.name.strip() or ""

    if x_moltbook_identity:
        profile = await _verify_moltbook(x_moltbook_identity)
        provider = "moltbook"
        external_id = str(profile["id"])
        name = name or str(profile.get("name") or "moltbook-agent")
        verified = True
    elif req.moltos_agent_id:
        provider = "moltos"
        external_id = req.moltos_agent_id.strip()
        profile = await _molt_os_public_profile(external_id)
        name = name or str(profile.get("name") or profile.get("handle") or external_id)
        if req.moltos_challenge and req.moltos_signature:
            verified = await _verify_moltos_signature(
                external_id, req.moltos_challenge, req.moltos_signature
            )
    else:
        # Generic AgentSkills/HTTP clients send a locally persisted, non-secret
        # client id so retries/restarts resolve to the same Moltwork worker and
        # do not create a new wallet every time.
        provider = "moltwork"
        external_id = req.client_id.strip() or f"native:{uuid.uuid4().hex}"
        name = name or f"worker-{uuid.uuid4().hex[:6]}"

    worker_id = _create_identity(provider, external_id, name, verified, profile)
    wallet = await _provision_wallet(worker_id)
    human_task = _get_or_create_safety_task(worker_id, wallet)

    sid = f"go-{uuid.uuid4().hex[:12]}"
    now = time.time()
    conn = get_db()
    conn.execute(
        "INSERT INTO go_sessions VALUES (?,?,?,?,?,?)",
        (sid, worker_id, req.runtime or "generic", "ready", now, now),
    )
    conn.commit()
    conn.close()

    # The caller owns the runtime loop. Moltwork supplies identity, wallet state,
    # policy and market data; WorkerKit/get-me-money executes the job.
    return {
        "ok": True,
        "worker": {"id": worker_id, "name": name},
        "identity": {
            "provider": provider,
            "external_id": external_id,
            "verified": verified,
            "reputation": {
                "karma": profile.get("karma") if provider == "moltbook" else None,
                "tap_score": profile.get("tap_score") if provider == "moltos" else None,
            },
        },
        "wallet": wallet,
        "human_task": human_task,
        "session": {"id": sid, "status": "ready", "runtime": req.runtime or "generic"},
        "next": "start_work_loop",
    }


@app.get("/api/go/status/{worker_id}")
def go_status(worker_id: str):
    conn = get_db()
    identity = conn.execute("SELECT * FROM go_identities WHERE worker_id=?", (worker_id,)).fetchone()
    wallet = conn.execute("SELECT * FROM go_wallets WHERE worker_id=?", (worker_id,)).fetchone()
    sessions = conn.execute(
        "SELECT * FROM go_sessions WHERE worker_id=? ORDER BY created_at DESC LIMIT 5",
        (worker_id,),
    ).fetchall()
    tasks = conn.execute(
        "SELECT * FROM go_human_tasks WHERE worker_id=? AND status='pending' ORDER BY created_at DESC",
        (worker_id,),
    ).fetchall()
    conn.close()
    if not identity:
        raise HTTPException(404, "worker not activated with Moltwork Go")
    out_wallet = dict(wallet) if wallet else None
    if out_wallet:
        out_wallet["policy"] = json.loads(out_wallet.pop("policy_json"))
    return {
        "worker_id": worker_id,
        "identity": {k: v for k, v in dict(identity).items() if k != "profile_json"},
        "wallet": out_wallet,
        "sessions": [dict(r) for r in sessions],
        "pending_human_tasks": [
            {**dict(r), "metadata": json.loads(r["metadata_json"])} for r in tasks
        ],
    }
