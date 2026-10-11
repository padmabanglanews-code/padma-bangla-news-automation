"""Command-line entry point for the local read-only dashboard.

Usage:
  PADMA_DASHBOARD_TOKEN='set-a-long-random-secret' python -m manager.run_dashboard

The token must be supplied through the environment, never committed to source.
The server binds to 127.0.0.1 only and does not run news collection or publishing.
"""
import os

from .dashboard_http import serve_local_dashboard


def main():
    token = os.getenv("PADMA_DASHBOARD_TOKEN", "")
    if len(token) < 24:
        raise SystemExit("Set PADMA_DASHBOARD_TOKEN to a random secret of at least 24 characters.")
    print("Padma Bangla News read-only dashboard: http://127.0.0.1:8765/")
    print("API access requires Authorization: Bearer <PADMA_DASHBOARD_TOKEN>.")
    print("Read-only mode: no RSS run, AI call, Blogger write, schedule or publishing.")
    serve_local_dashboard(host="127.0.0.1", port=int(os.getenv("PADMA_DASHBOARD_PORT", "8765")), token=token)


if __name__ == "__main__":
    main()
