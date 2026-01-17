#!/usr/bin/env bash
set -e

CANARY_NAME="empire-api-v1-canary"
PRIMARY_NAME="empire-api-v1"

echo "🚀 Starting canary deployment for $CANARY_NAME"

# Deploy canary
modal deploy modal_orchestrator.py --name $CANARY_NAME --stream-logs

echo "⏳ Waiting 30s for canary to warm up..."
sleep 30

echo "📡 Running smoke tests against canary"
CANARY_URL="https://nearmiss1193-afk--${CANARY_NAME}-orchestration-api.modal.run"

# Run smoke tests
python tests/smoke_test.py --base-url "$CANARY_URL"

if [ $? -eq 0 ]; then
  echo "✔ Canary OK — promoting to primary"
  # Deploy as primary (overwrites)
  modal deploy modal_orchestrator.py --name $PRIMARY_NAME --stream-logs
  # Clean up canary
  modal app stop $CANARY_NAME 2>/dev/null || true
  echo "✅ Canary promoted successfully"
  exit 0
else
  echo "❌ Canary failed — rolling back"
  modal app stop $CANARY_NAME 2>/dev/null || true
  exit 1
fi
