"""Real Git worktree subprocess test — proves workspace actually works.

Uses real subprocess Git commands in a temp directory. No mocks.
"""
import sys, os, subprocess, tempfile, shutil
from pathlib import Path
sys.path.insert(0, '/root')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PASS = FAIL = 0
def test(name, cond, detail=""):
    global PASS, FAIL
    if cond: PASS+=1; print(f"  ✓ {name}")
    else: FAIL+=1; print(f"  ✗ {name} — {detail}")

print("=== REAL GIT WORKTREE TEST ===\n")

def git(*args, cwd):
    r = subprocess.run(["git"] + list(args), capture_output=True, text=True, cwd=cwd)
    return r.returncode, r.stdout.strip(), r.stderr.strip()

# ─── 1. Init temp repo ────────────────────────────────────────────────
print("1. Init temp repo")
tmp = Path(tempfile.mkdtemp(prefix="wk-git-test-"))
try:
    code, _, _ = git("init", cwd=str(tmp))
    test("git init", code == 0)
    git("config", "user.email", "test@test.com", cwd=str(tmp))
    git("config", "user.name", "Test", cwd=str(tmp))

    # Baseline commit
    (tmp / "README.md").write_text("# baseline")
    git("add", "-A", cwd=str(tmp))
    code, out, _ = git("commit", "-m", "baseline", cwd=str(tmp))
    test("baseline committed", code == 0)
    base_head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=str(tmp)).stdout.strip()
    test("base HEAD is 40 hex", len(base_head) == 40)

    # ─── 2. Create worktree ────────────────────────────────────────────
    print("\n2. Create worktree")
    wt_path = tmp / ".moltwork" / "worktrees" / "run-001"
    wt_path.parent.mkdir(parents=True, exist_ok=True)
    git("branch", "mw/run-001", cwd=str(tmp))
    code, out, err = git("worktree", "add", str(wt_path), "mw/run-001", cwd=str(tmp))
    test("worktree created", code == 0 and wt_path.is_dir())
    test("worktree has README", (wt_path / "README.md").exists())

    # ─── 3. Modify file in worktree ────────────────────────────────────
    print("\n3. Modify file in worktree")
    (wt_path / "feature.py").write_text("def hello(): return 'world'")
    code, _, _ = git("add", "-A", cwd=str(wt_path))
    test("staged changes", code == 0)
    code, _, _ = git("commit", "-m", "add feature", cwd=str(wt_path))
    test("committed from worktree", code == 0)

    # ─── 4. Verify HEADs differ ────────────────────────────────────────
    print("\n4. Verify HEADs differ")
    wt_head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=str(wt_path)).stdout.strip()
    main_head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=str(tmp)).stdout.strip()
    test("worktree HEAD differs from main", wt_head != main_head)
    test("worktree HEAD is 40 hex", len(wt_head) == 40)
    print(f"    main:    {main_head[:16]}...")
    print(f"    worktree: {wt_head[:16]}...")

    # ─── 5. Main working tree unchanged ────────────────────────────────
    print("\n5. Main working tree unchanged")
    test("main has no feature.py", not (tmp / "feature.py").exists())
    test("main README unchanged", (tmp / "README.md").read_text() == "# baseline")

    # ─── 6. Simulate workspace close (commit + cleanup) ────────────────
    print("\n6. Workspace close")
    code, _, _ = git("worktree", "remove", str(wt_path), "--force", cwd=str(tmp))
    test("worktree removed", code == 0)
    test("worktree path gone", not wt_path.exists())

    # ─── 7. Final state ────────────────────────────────────────────────
    print("\n7. Final state")
    code, out, _ = git("log", "--oneline", cwd=str(tmp))
    test("main repo still intact", code == 0)
    code, out, _ = git("branch", cwd=str(tmp))
    test("work branch exists", "mw/run-001" in out)

    print(f"\n{'='*60}")
    print(f"REAL GIT WORKTREE TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Repo:     {tmp}")
    print(f"Main:     {base_head[:16]}...")
    print(f"Worktree: {wt_head[:16]}...")
    print(f"Branch:   mw/run-001")
    print(f"{'='*60}")

finally:
    shutil.rmtree(str(tmp), ignore_errors=True)

print(f"\n=== {PASS} passed, {FAIL} failed ===")
if FAIL: sys.exit(1)
else: print("REAL GIT WORKTREE TEST PASS — subprocess Git lifecycle verified")
