# Context Engine: Elastic-side take-away

The Elastic pieces of the **Context Engine / Knowledge Retrieval** workshop, for running in your own Elastic Cloud Serverless project. The workshop's agent layer (Agent Builder) is not included: bring your own agent (for example in Azure AI Foundry) and point it at the AI Index.

## What is here

| Path | What it is |
|---|---|
| `docs/ai-index-setup.md` | Step-by-step: create the AI Index, add sources, generate Knowledge Indicators, inspect/edit them, and how an agent should use them |
| `workflows/precision-index-metadata-kis.yml` | The Kibana Workflow you paste into the Context Engine "Create automation" editor. Profiles each index with an LLM and writes one KI per index |
| `workflows/plan-b-write-kis-no-llm.yml` | Fallback workflow that writes the same three KIs with no LLM step |
| `data/crm_dataset.py`, `support_tickets_dataset.py`, `kb_articles_dataset.py` | Deterministic (seed 42) generators for the dataset. Each also indexes its data |
| `data/load_data.sh` | Runs all three generators in the right order and prints document counts |

## The dataset (fictional "Precision Labs")

| Index | Docs | Notes |
|---|---|---|
| `precision-crm-accounts` | 500 | tier, `arr` (annual recurring revenue, USD), churn risk, renewal date, owner |
| `precision-support-tickets` | 3,000 | priority, category, status; `account_id` joins to `customer_id` in accounts |
| `precision-kb-articles` | 150 | knowledge-base articles by category |

No data files are committed; it is generated at load time, so the repo stays small (under 100 KB total).

## Order to run on a fresh Serverless trial

1. **Create an Elasticsearch Serverless project** and an API key that can create indices and write documents.
2. **Load the data** (Python 3 with `pip install elasticsearch`):
   ```bash
   export ES_URL="https://<your-project-endpoint>"
   export ES_API_KEY="<your-api-key>"
   cd data && ./load_data.sh
   ```
   Expect counts of 500 / 3000 / 150. The script deletes and recreates the three `precision-*` indices.
3. **Create the AI Index, add sources, run the workflow**: follow [`docs/ai-index-setup.md`](docs/ai-index-setup.md). Before running the workflow, replace `<YOUR_LLM_CONNECTOR_ID>` in the YAML with a chat-completion connector id from your project.
4. **Confirm 3 Knowledge Indicators** exist in `ai-index-idx-precision-corpus`.
5. **Connect your agent** (yours, not covered here). Have it retrieve KIs with the Context Engine tools (`list_ai_indices`, `describe_ai_index`, `query_ai_indices`) first, then run targeted ES|QL against the `precision-*` indices.

## Notes

- Features used (Context Engine, AI Index, Kibana Workflows, `context-engine.createKi`) are recent and may change; the YAML was last verified on a Serverless project during the workshop build.
- Nothing here contains credentials, cluster URLs or connector ids; supply your own.
