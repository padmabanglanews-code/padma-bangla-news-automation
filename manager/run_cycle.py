"""Guarded manual entry point for the Padma Bangla News agent.

All live stages default off. This command is intended for explicit manual runs
from GitHub Actions. It never publishes and writes only review candidates.
"""
import json
import os
from pathlib import Path

from .dashboard_service import run_dashboard_cycle
from .persistent_dashboard import PersistentDashboardDraftStore
from .supabase_dashboard import SupabaseDashboardDraftStore


def _enabled(name):
    return os.getenv(name, "false").strip().lower() == "true"


def main():
    live_rss = _enabled("PADMA_RUN_LIVE_RSS")
    generate_ai = _enabled("PADMA_RUN_OPENROUTER")
    create_blogger_drafts = _enabled("PADMA_CREATE_BLOGGER_DRAFTS")

    if generate_ai and not live_rss:
        raise SystemExit("Refusing run: OpenRouter requires PADMA_RUN_LIVE_RSS=true")
    if create_blogger_drafts and not generate_ai:
        raise SystemExit("Refusing run: Blogger drafts require PADMA_RUN_OPENROUTER=true")

    if os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_SERVICE_ROLE_KEY"):
        store = SupabaseDashboardDraftStore()
    else:
        store = PersistentDashboardDraftStore(
            os.getenv("PADMA_DASHBOARD_STORE_PATH", "manager/data/dashboard_drafts.json")
        )

    result = run_dashboard_cycle(
        live_rss=live_rss,
        generate_ai=generate_ai,
        create_blogger_drafts=create_blogger_drafts,
        max_stories=min(max(int(os.getenv("PADMA_MAX_STORIES", "5")), 1), 8),
        store=store,
    )
    output = Path(os.getenv("PADMA_CYCLE_OUTPUT", "manager-cycle-result.json"))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "mode": result.get("mode"),
        "draft_count": result.get("dashboard", {}).get("draft_count", 0),
        "published": False,
        "blogger_contacted": result.get("pipeline", {}).get("blogger_contacted", False),
        "output_file": str(output),
    }, ensure_ascii=False))
    if result.get("pipeline", {}).get("ai_errors"):
        print("Some AI candidates failed; inspect the private workflow artifact.")
    if result.get("pipeline", {}).get("blogger_results"):
        print("Blogger draft results are recorded; no publishing was performed.")


if __name__ == "__main__":
    main()
