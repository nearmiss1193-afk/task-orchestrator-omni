#!/usr/bin/env bash
set -e

echo "🚨 Running rollback to last stable Modal deployment"

# Fetch list of past deploy versions
modal app versions empire-api-v1 > versions.txt 2>/dev/null || echo "No versions found"

# Find the second-to-latest (assuming latest failed)
LAST_GOOD=$(grep -Eo "version: [0-9]+" versions.txt 2>/dev/null | sort -n | tail -n2 | head -n1 | awk '{print $2}')

if [ -z "$LAST_GOOD" ]; then
  echo "⚠️ Could not determine last good version, attempting redeploy..."
  modal deploy modal_orchestrator.py --name empire-api-v1
  exit $?
fi

echo "↩ Rolling back to version $LAST_GOOD"
modal app deploy-version empire-api-v1 $LAST_GOOD

if [ $? -eq 0 ]; then
  echo "✅ Rollback successful"
else
  echo "❌ Rollback failed"
  exit 1
fi
