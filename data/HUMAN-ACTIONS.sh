#!/bin/bash
# Oracle Agent — Human Action Queue
# Run each command after completing the human step

echo "=== ORACLE HUMAN QUEUE ==="
echo ""

# 1. METACULUS (CRITICAL - Sep 6 deadline)
echo "1. METACULUS TOKEN"
echo "   Go to: https://www.metaculus.com/futureeval/participate/"
echo "   Create bot token, then run:"
echo "   agent-vault vault credential set METACULUS_TOKEN='YOUR_TOKEN' --vault oracle"
echo ""

# 2. WALLET (unlocks AgentPact)
echo "2. BASE WALLET ADDRESS"
echo "   Go to: https://app.debank.com or create a Base wallet"
echo "   Copy your 0x... address, then run:"
echo "   agent-vault vault credential set BASE_WALLET_ADDRESS='0x...' --vault oracle"
echo ""

# 3. MOLTJOBS
echo "3. MOLTJOBS API KEY"
echo "   Go to: https://moltjobs.io"
echo "   Sign in → Settings → API Keys → Create"
echo "   agent-vault vault credential set MOLTJOBS_API_KEY='mj_live_...' --vault oracle"
echo ""

# 4. DEALWORK
echo "4. DEALWORK ACTIVATION"
echo "   Open: https://dealwork.ai/login?redirect=%2Fdashboard%2Fagents%2Fconnect%3Ftoken%3DVMMxtlN14tL5a57RBR3zEBX3tFr3jNBnLaH01PTU2R0"
echo "   Login → Authorize → Done"
echo ""

# 5. KAGGLE
echo "5. KAGGLE API KEY"
echo "   Go to: https://www.kaggle.com/settings"
echo "   Create API Token → downloads kaggle.json"
echo "   agent-vault vault credential set KAGGLE_USERNAME='YOUR_USERNAME' --vault oracle"
echo "   agent-vault vault credential set KAGGLE_KEY='YOUR_KEY' --vault oracle"
echo ""

echo "=== After running commands, tell the agent: 'vault updated' ==="
