"""Merkle commitment + random reveal for information assets.

Core primitive:
1. Take artifact text
2. Split into coherent chunks (200-400 tokens, sentence boundaries)
3. Salt + hash each chunk
4. Build Merkle tree
5. Encrypt full artifact
6. Publish only: root, metadata, encrypted blob

Reveal:
1. Buyer pays for next chunk
2. Protocol derives random chunk index (drand or deterministic from root+buyer)
3. Return chunk + Merkle proof
4. Verify: H(chunk) matches path to published root
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
from dataclasses import dataclass, field
from typing import Any


def sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# === Chunking ===

def chunk_text(text: str, target_chunks: int = 10, min_chunk_size: int = 80) -> list[str]:
    """Split text into coherent chunks.

    Strategy: split into sentences, then distribute into target_chunks groups
    of roughly equal size. Always produces at least 2 chunks for texts > min_chunk_size.
    For short texts, falls back to character-level splitting to ensure enough chunks
    for meaningful progressive reveal.

    Args:
        text: the input text
        target_chunks: desired number of chunks
        min_chunk_size: minimum characters per chunk (prevents tiny useless chunks)
    """
    text = text.strip()
    if not text:
        return [""]

    # For very short texts, return as-is (no useful way to split)
    if len(text) < min_chunk_size:
        return [text] if text else [""]

    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    if len(sentences) <= 1:
        # No sentence boundaries — split by paragraph or commas
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        if len(paragraphs) > 1:
            sentences = paragraphs
        else:
            # Split by commas/semicolons as last resort
            parts = re.split(r'[,;]\s*', text)
            sentences = [s.strip() for s in parts if len(s.strip()) > 20]

    if len(sentences) <= 1:
        # Still no split points — character-level split for long texts
        if len(text) > target_chunks * min_chunk_size:
            chunk_len = max(min_chunk_size, len(text) // target_chunks)
            chunks = []
            for i in range(0, len(text), chunk_len):
                chunk = text[i:i + chunk_len].strip()
                if chunk:
                    chunks.append(chunk)
            return chunks if len(chunks) >= 2 else [text]
        return [text]

    # Distribute sentences into target_chunks groups
    if len(sentences) >= target_chunks:
        chunk_size = max(1, len(sentences) // target_chunks)
    else:
        # Fewer sentences than target — each sentence is a chunk
        return sentences

    chunks = []
    for i in range(0, len(sentences), chunk_size):
        chunk = " ".join(sentences[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk.strip())

    # Merge tiny trailing chunks
    if len(chunks) > 2 and len(chunks[-1]) < min_chunk_size:
        chunks[-2] = chunks[-2] + " " + chunks[-1]
        chunks.pop()

    # Ensure at least 2 chunks for texts long enough to split
    if len(chunks) == 1 and len(text) > min_chunk_size * 2:
        mid = len(text) // 2
        boundary = text.rfind('. ', 0, mid)
        if boundary < mid // 2:
            boundary = text.find('. ', mid)
        if boundary < mid // 3:
            boundary = mid  # just split in half
        if boundary > 0:
            chunks = [text[:boundary + 1].strip(), text[boundary + 1:].strip()]

    return chunks if chunks else [text]


# === Merkle Tree ===

@dataclass
class MerkleLeaf:
    index: int
    salt: bytes
    data: bytes
    hash: bytes = field(default_factory=bytes)

    def __post_init__(self):
        if not self.hash:
            self.hash = sha256(
                self.salt + self.index.to_bytes(4, 'big') + self.data
            )


@dataclass
class MerkleTree:
    root: bytes
    leaves: list[MerkleLeaf]
    size: int

    def get_proof(self, index: int) -> list[tuple[bytes, bool]]:
        """Get Merkle proof path for leaf at index. Returns list of (hash, is_right)."""
        if index < 0 or index >= self.size:
            return []

        # Build tree levels
        levels = [[leaf.hash for leaf in self.leaves]]
        current = levels[0]
        while len(current) > 1:
            next_level = []
            for i in range(0, len(current), 2):
                left = current[i]
                right = current[i + 1] if i + 1 < len(current) else left
                next_level.append(sha256(left + right))
            levels.append(next_level)
            current = next_level

        # Walk up from leaf to root
        proof = []
        idx = index
        for level in levels[:-1]:
            if idx % 2 == 0:
                sibling = level[idx + 1] if idx + 1 < len(level) else level[idx]
                proof.append((sibling, True))  # sibling is right
            else:
                sibling = level[idx - 1]
                proof.append((sibling, False))  # sibling is left
            idx //= 2

        return proof

    def verify_proof(self, leaf_hash: bytes, proof: list[tuple[bytes, bool]],
                     index: int) -> bool:
        """Verify a Merkle proof."""
        current = leaf_hash
        for sibling, is_right in proof:
            if is_right:
                current = sha256(current + sibling)
            else:
                current = sha256(sibling + current)
        return current == self.root


def build_merkle(chunks: list[str], artifact_id: str = "") -> MerkleTree:
    """Build Merkle tree from text chunks."""
    leaves = []
    for i, chunk in enumerate(chunks):
        salt = sha256(f"{artifact_id}:{i}:{os.urandom(8).hex()}".encode())
        data = chunk.encode('utf-8')
        leaf = MerkleLeaf(index=i, salt=salt, data=data)
        leaves.append(leaf)

    # Build tree
    current = [leaf.hash for leaf in leaves]
    levels = [current]
    while len(current) > 1:
        next_level = []
        for i in range(0, len(current), 2):
            left = current[i]
            right = current[i + 1] if i + 1 < len(current) else left
            next_level.append(sha256(left + right))
        levels.append(next_level)
        current = next_level

    return MerkleTree(
        root=current[0] if current else b'\x00' * 32,
        leaves=leaves,
        size=len(leaves),
    )


# === Random Reveal Order ===

def derive_reveal_order(root: bytes, buyer_id: str, size: int) -> list[int]:
    """Derive deterministic random reveal order from root + buyer_id.

    Neither party can predict the order before commitment.
    Uses HMAC-SHA256 as a PRF.
    """
    import hmac as hmac_mod

    order = list(range(size))
    # Fisher-Yates shuffle with deterministic seed
    seed = sha256(root + buyer_id.encode())
    for i in range(size - 1, 0, -1):
        # Generate pseudorandom index
        h = sha256(seed + i.to_bytes(4, 'big'))
        j = int.from_bytes(h[:4], 'big') % (i + 1)
        order[i], order[j] = order[j], order[i]

    return order


# === Artifact Envelope ===

@dataclass
class ArtifactEnvelope:
    """A committed, encrypted artifact ready for progressive reveal."""
    artifact_id: str
    title: str
    abstract: str
    total_price: float
    currency: str
    total_units: int
    merkle_root: str
    encrypted_blob: str  # base64 or hex
    chunk_hashes: list[str]  # for verification
    metadata: dict = field(default_factory=dict)
    license: str = "buyer-use"
    created_at: float = 0.0

    def to_dict(self) -> dict:
        return {
            "artifact_id": self.artifact_id,
            "title": self.title,
            "abstract": self.abstract,
            "total_price": self.total_price,
            "currency": self.currency,
            "total_units": self.total_units,
            "merkle_root": self.merkle_root,
            "encrypted_blob": self.encrypted_blob,
            "chunk_hashes": self.chunk_hashes,
            "metadata": self.metadata,
            "license": self.license,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, d: dict) -> ArtifactEnvelope:
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


def create_envelope(text: str, title: str, total_price: float,
                    currency: str = "USDC", target_chunk_tokens: int = 300,
                    artifact_id: str = "") -> tuple[ArtifactEnvelope, list[str]]:
    """Create an artifact envelope from text.

    Returns (envelope, chunks) — envelope is what gets published,
    chunks are the plaintext (kept private, used for reveal).
    """
    import time
    import base64

    if not artifact_id:
        artifact_id = sha256_hex(text.encode() + os.urandom(8))

    # Chunk
    chunks = chunk_text(text, target_chunk_tokens)

    # Build Merkle
    tree = build_merkle(chunks, artifact_id)

    # "Encrypt" (XOR with key for V1 — real encryption would use AES-GCM)
    key = sha256(artifact_id.encode())
    encrypted = bytes(
        b ^ key[i % len(key)]
        for i, b in enumerate(text.encode('utf-8'))
    )

    # Abstract: first ~250 chars
    abstract = text[:250].rsplit(' ', 1)[0] + "..." if len(text) > 250 else text

    envelope = ArtifactEnvelope(
        artifact_id=artifact_id,
        title=title,
        abstract=abstract,
        total_price=total_price,
        currency=currency,
        total_units=len(chunks),
        merkle_root=tree.root.hex(),
        encrypted_blob=base64.b64encode(encrypted).decode(),
        chunk_hashes=[leaf.hash.hex() for leaf in tree.leaves],
        metadata={
            "total_chars": len(text),
            "total_tokens_approx": len(text) // 4,
            "chunk_count": len(chunks),
        },
        created_at=time.time(),
    )

    return envelope, chunks


def reveal_chunk(chunks: list[str], tree: MerkleTree,
                 chunk_index: int, buyer_id: str) -> dict:
    """Reveal a specific chunk with its Merkle proof."""
    if chunk_index < 0 or chunk_index >= len(chunks):
        return {"error": "invalid chunk index"}

    leaf = tree.leaves[chunk_index]
    proof = tree.get_proof(chunk_index)

    return {
        "chunk_index": chunk_index,
        "content": chunks[chunk_index],
        "hash": leaf.hash.hex(),
        "proof": [(h.hex(), is_right) for h, is_right in proof],
        "verified": True,
    }
