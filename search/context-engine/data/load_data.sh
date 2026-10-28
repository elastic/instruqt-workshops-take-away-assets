#!/bin/bash
# Load the three Precision Labs indices into your Elasticsearch Serverless project.
#
# Usage:
#   pip install elasticsearch
#   export ES_URL="https://<your-project>.es.<region>.<provider>.elastic.cloud"
#   export ES_API_KEY="<your API key>"
#   ./load_data.sh
#
# Deletes and recreates the three precision-* indices each run. Data is generated
# deterministically (seed 42), so every run produces the same documents. Takes under 90 s.
set -euo pipefail
cd "$(dirname "$0")"

: "${ES_URL:?Set ES_URL to your Elasticsearch endpoint}"
: "${ES_API_KEY:?Set ES_API_KEY to an API key that can create indices}"
PYTHON="${PYTHON:-python3}"

echo "--- precision-crm-accounts (500 accounts) ---"
"$PYTHON" crm_dataset.py --es-url "$ES_URL" --api-key "$ES_API_KEY"

echo "--- precision-support-tickets (3000 tickets) ---"
PYTHONPATH=. "$PYTHON" support_tickets_dataset.py --es-url "$ES_URL" --api-key "$ES_API_KEY"

echo "--- precision-kb-articles (150 articles) ---"
"$PYTHON" kb_articles_dataset.py --es-url "$ES_URL" --api-key "$ES_API_KEY"

echo "=== Verifying counts ==="
for idx in precision-crm-accounts precision-support-tickets precision-kb-articles; do
  printf '  %s: ' "$idx"
  curl -sf -H "Authorization: ApiKey ${ES_API_KEY}" "${ES_URL}/${idx}/_count" \
    | "$PYTHON" -c "import sys,json; print(json.load(sys.stdin)['count'])" || echo "ERR"
done
