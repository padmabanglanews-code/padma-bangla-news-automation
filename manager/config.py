from dataclasses import dataclass
import os
from pathlib import Path

@dataclass(frozen=True)
class Settings:
    history_path: Path = Path(os.getenv("PADMA_MANAGER_HISTORY", "manager/data/history.json"))
    max_stories: int = int(os.getenv("PADMA_MANAGER_MAX_STORIES", "20"))
    dry_run: bool = os.getenv("PADMA_MANAGER_DRY_RUN", "true").strip().lower() not in {"0", "false", "no"}

def get_settings() -> Settings:
    return Settings()
