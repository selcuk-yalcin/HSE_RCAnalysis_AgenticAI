"""
Celery pipeline canlı ilerleme satırları — worker loglarının UI'a akması için.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional


def clean_activity_line(line: str) -> str:
    """Emoji ve fazla boşlukları sadeleştirir; boş satırları atar."""
    text = str(line or "").strip()
    if not text:
        return ""
    if set(text) <= {"=", "-", "_"}:
        return ""
    return text


class PipelineProgressReporter:
    """Celery task.update_state ile activity_lines biriktirir."""

    def __init__(
        self,
        update_fn: Callable[[Dict[str, Any]], None],
        *,
        incident_id: str = "",
        tenant_id: str = "default",
        max_lines: int = 60,
    ):
        self._update = update_fn
        self._incident_id = incident_id
        self._tenant_id = tenant_id
        self._max_lines = max(10, int(max_lines))
        self.lines: List[str] = []
        self._stage = "investigate"
        self._progress = 10

    def emit(
        self,
        line: str,
        *,
        stage: Optional[str] = None,
        progress: Optional[int] = None,
        message: Optional[str] = None,
    ) -> None:
        clean = clean_activity_line(line)
        if not clean:
            return
        if self.lines and self.lines[-1] == clean:
            return
        self.lines.append(clean)
        if len(self.lines) > self._max_lines:
            self.lines = self.lines[-self._max_lines :]
        if stage:
            self._stage = stage
        if progress is not None:
            self._progress = int(progress)
        meta: Dict[str, Any] = {
            "incident_id": self._incident_id,
            "tenant_id": self._tenant_id,
            "stage": self._stage,
            "progress": self._progress,
            "message": message or clean[:120],
            "activity_lines": list(self.lines),
            "latest_activity": clean,
        }
        self._update(meta)


def celery_progress_reporter(task, incident_id: str, tenant_id: str) -> PipelineProgressReporter:
    """Celery bind=True task için reporter fabrikası."""

    def _push(meta: Dict[str, Any]) -> None:
        task.update_state(state="PROGRESS", meta=meta)

    return PipelineProgressReporter(
        _push,
        incident_id=incident_id,
        tenant_id=tenant_id,
    )
