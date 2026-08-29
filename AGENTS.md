# AGENTS.md — WorkerKit Operating Rules

## Commands

```bash
# Start background task
setsid nohup CMD > /tmp/output.log 2>&1 &
echo "PID: $!"

# Check status
ps aux | grep CMD | grep -v grep

# Kill by PID (NEVER pkill)
kill PID
```

## Rules

1. **Fail fast** — if something doesn't work in 3 attempts, stop and report
2. **Background tasks** — always `setsid nohup CMD > /tmp/log 2>&1 &`
3. **Kill by PID** — find PID first, then `kill PID`. NEVER `pkill`.
4. **No long timeouts** — max 30s for any single command unless explicitly told otherwise
5. **Log everything** — write to `/root/workerkit/data/logs/`
6. **Test before claiming** — run the code, don't assume it works

## Test Commands

```bash
# Run all tests
cd /root/workerkit && for t in tests/test_*.py; do python3 "$t" 2>&1 | tail -3; done

# Run single test
cd /root/workerkit && python3 tests/test_ethonline.py 2>&1

# Start Letta server
cd /root/workerkit/services/runtime-letta && setsid nohup node --import tsx src/index.ts > /tmp/letta-server.log 2>&1 &
echo "PID: $!"
sleep 3
curl -s http://localhost:3000/health
```

## Model Config

Provider: opencode-go
Model: opencode-go/mimo-v2.5
Backend: local
