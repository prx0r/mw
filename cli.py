"""Moltwork Go CLI."""
import asyncio
import sys
sys.path.insert(0, '/root')
sys.path.insert(0, '/root/workerkit')

from mwgo.go import MoltworkGo


def main():
    if len(sys.argv) < 2:
        print("mwgo — Give an agent a dollar, it tries to make money.")
        print()
        print("Usage:")
        print("  mwgo go              Start working")
        print("  mwgo status          Show status")
        print("  mwgo go --budget 5   Start with $5")
        return

    cmd = sys.argv[1]

    if cmd == "go":
        budget = 1.0
        for i, arg in enumerate(sys.argv):
            if arg == "--budget" and i + 1 < len(sys.argv):
                budget = float(sys.argv[i + 1])
        go = MoltworkGo(balance=budget)
        result = asyncio.run(go.work())

    elif cmd == "status":
        go = MoltworkGo()
        s = go.status()
        print(f"Balance: ${s['balance']:.2f}")
        print(f"Earned: ${s['earned']:.2f}")
        print(f"Spent: ${s['spent']:.2f}")
        print(f"Jobs: {s['jobs']}")
        print(f"Market: {s['market']}")


if __name__ == "__main__":
    main()
