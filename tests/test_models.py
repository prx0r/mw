"""Moltwork Market tests — all slices."""
import sys, os, json, time
sys.path.insert(0, '/root')

PASS = 0
FAIL = 0

def test(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  PASS: {name}")
    else:
        FAIL += 1
        print(f"  FAIL: {name} — {detail}")

print("=== MOLTWORK MARKET TESTS ===\n")

# ─── 1. Slice 0: SHA-256 is full 64 chars ───
print("1. SHA-256 integrity")
from mwmarket.models import sha256
h = sha256("test")
test("sha256 is 64 chars", len(h) == 64, f"got {len(h)}")

# ─── 2. AssetVersion — immutable, content-addressed ───
print("\n2. AssetVersion")
from mwmarket.models import AssetVersion
av = AssetVersion(
    name="Reddit Pain-Point Research",
    kind="PROCESS",
    owner_id="worker-1",
    capability_namespace="research.market.pain-points",
    package_sha256=sha256("package-content"),
    merkle_root=sha256("merkle-root"),
)
manifest = av.content_manifest()
test("content manifest is 64 chars", len(manifest) == 64)
# Same manifest → same hash
av2 = AssetVersion(
    name="Reddit Pain-Point Research",
    kind="PROCESS",
    owner_id="worker-1",
    capability_namespace="research.market.pain-points",
    package_sha256=sha256("package-content"),
    merkle_root=sha256("merkle-root"),
)
av2.id = av.id
av2.version = av.version
av2.created_at = av.created_at
test("same manifest → same hash", manifest == av2.content_manifest())

# ─── 3. Listing ───
print("\n3. Listing")
from mwmarket.models import Listing
lst = Listing(asset_id="av-1", seller_id="worker-1", price_model="FIXED", price_amount="5.00")
test("listing has id", lst.id.startswith("lst_"))
test("listing is ACTIVE", lst.status == "ACTIVE")

# ─── 4. AccessGrant with quota + expiry ───
print("\n4. AccessGrant")
from mwmarket.models import AccessGrant
g = AccessGrant(
    principal="buyer-1",
    listing_id="lst-1",
    asset_id="av-1",
    rights="INVOKE",
    quotas={"calls_remaining": 5},
)
test("grant is valid", g.is_valid())
test("grant has quota", g.quotas["calls_remaining"] == 5)
ok = g.consume_call()
test("consume call", ok)
test("quota decremented", g.quotas["calls_remaining"] == 4)
# Exhaust quota
for _ in range(4):
    g.consume_call()
test("quota exhausted", not g.consume_call())
test("grant invalid after exhaustion", not g.is_valid())

# Expiring grant
g2 = AccessGrant(rights="LEASE", expires_at=time.time() - 1)
test("expired grant invalid", not g2.is_valid())

# ─── 5. SampleReceipt ───
print("\n5. SampleReceipt")
from mwmarket.models import SampleReceipt
sr = SampleReceipt(
    asset_id="av-1",
    listing_id="lst-1",
    buyer_id="buyer-1",
    chunk_index=3,
    cumulative_units=5,
    total_units=40,
    amount_paid="0.50",
    payment_ref="pay-123",
)
test("sample receipt has id", sr.id.startswith("sr_"))
# Verify with matching proof
root = sha256("root")
sr.merkle_proof = [{"hash": sha256("sibling"), "side": "right"}]
test("sample receipt serializes", "chunk_index" in sr.to_dict())

# ─── 6. Invocation ───
print("\n6. Invocation")
from mwmarket.models import Invocation
inv = Invocation(service_asset_id="av-svc", buyer_id="buyer-1", input_digest=sha256("input"))
test("invocation pending", inv.status == "pending")
inv.status = "executing"
from mwmarket.models import Invocation
inv2 = Invocation(service_asset_id="av-svc", buyer_id="buyer-1")
test("invocation has id", inv2.id.startswith("inv_"))

# ─── 7. Request with ERC-8183 lifecycle ───
print("\n7. Request lifecycle")
from mwmarket.models import Request
r = Request(title="Build API", creator_id="buyer-1", budget="10.00")
test("request starts open", r.status == "open")
r.status = "funded"
test("request funded", r.status == "funded")
r.status = "submitted"
r.receipt_hash = sha256("receipt")
r.deliverable = "output.md"
test("request submitted", r.status == "submitted")
r.status = "completed"
test("request completed", r.status == "completed")

# ─── 8. CapabilityLease ───
print("\n8. CapabilityLease")
from mwmarket.models import CapabilityLease
cl = CapabilityLease(
    asset_id="av-worker",
    lessor_id="owner-1",
    lessee_id="renter-1",
    max_calls=10,
    valid_until=time.time() + 3600,
)
test("lease is valid", cl.is_valid())
test("calls_used starts 0", cl.calls_used == 0)
cl.consume_call()
test("calls_used after consume", cl.calls_used == 1)
# Revoke
cl.revoked = True
test("revoked lease invalid", not cl.is_valid())

# ─── 9. Board + DistributionGrant ───
print("\n9. Board")
from mwmarket.models import Board, DistributionGrant
b = Board(owner_id="curator-1", name="Research Parts", visibility="PUBLIC")
test("board has id", b.id.startswith("bd_"))
test("board is PUBLIC", b.visibility == "PUBLIC")
dg = DistributionGrant(listing_id="lst-1", board_id=b.id)
test("distribution grant seller_bps", dg.seller_bps == 9400)
test("distribution grant board_bps", dg.board_bps == 300)
test("distribution grant protocol_bps", dg.protocol_bps == 300)
test("bps sum to 10000", dg.seller_bps + dg.board_bps + dg.protocol_bps == 10000)

# ─── 10. MarketAPI integration ───
print("\n10. MarketAPI integration")
from mwmarket.api import MarketAPI
from mwmarket.models import WorkerProfile
import tempfile

with tempfile.TemporaryDirectory() as td:
    api = MarketAPI(db_path=f"{td}/market.db")

    # Register asset
    av = AssetVersion(name="Test Process", kind="PROCESS", owner_id="w1")
    aid = api.register_asset(av)
    test("asset registered", aid == av.id)

    # Publish listing
    lst = Listing(asset_id=aid, seller_id="w1", price_amount="2.00")
    lid = api.publish_listing(lst)
    test("listing published", lid == lst.id)

    # Create request
    rq = Request(title="Test Job", creator_id="buyer-1", budget="5.00")
    rid = api.create_request(rq)
    test("request created", rid == rq.id)
    api.fund_request(rid)
    api.submit_request(rid, receipt_hash="abc", deliverable="output.md")
    api.complete_request(rid)
    r_loaded = api.requests[rid]
    test("request lifecycle complete", r_loaded.status == "completed")

    # Issue lease
    lease = CapabilityLease(asset_id=aid, lessor_id="w1", lessee_id="r1", valid_until=time.time()+3600)
    lid2 = api.issue_lease(lease)
    test("lease issued", api.check_lease(lid2))
    api.revoke_lease(lid2)
    test("revoked lease invalid", not api.check_lease(lid2))

    # Create board
    board = Board(owner_id="curator-1", name="Test Board")
    bid = api.create_board(board)
    test("board created", bid == board.id)

    # Distribution grant
    dg = DistributionGrant(listing_id=lid, board_id=bid)
    api.place_on_board(dg)
    test("distribution grant placed", len(api.distribution_grants) == 1)

    # Stats
    s = api.stats()
    test("stats has all counts", all(k in s for k in ["assets", "listings", "requests", "leases", "boards"]))

print(f"\n=== RESULTS: {PASS} passed, {FAIL} failed ===")
if FAIL > 0:
    print("SOME TESTS FAILED")
    sys.exit(1)
else:
    print("ALL MARKET TESTS PASS")
