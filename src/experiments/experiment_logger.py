"""Persistência JSON/JSONL explícita para execuções experimentais."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from enum import Enum
import json
from pathlib import Path
from typing import Any, Mapping


def _json_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return _json_value(asdict(value))
    if isinstance(value, Mapping):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    return value


class ExperimentLogger:
    def __init__(self, run_directory: str | Path, metadata: Mapping[str, Any]) -> None:
        self.run_directory = Path(run_directory)
        self.run_directory.mkdir(parents=True, exist_ok=False)
        self.iterations_path = self.run_directory / "iterations.jsonl"
        self._write_json(self.run_directory / "metadata.json", metadata)

    def log_iteration(self, result: Any) -> None:
        with self.iterations_path.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(_json_value(result), ensure_ascii=False))
            stream.write("\n")

    def write_summary(self, summary: Mapping[str, Any]) -> None:
        self._write_json(self.run_directory / "summary.json", summary)

    @staticmethod
    def _write_json(path: Path, value: Any) -> None:
        path.write_text(
            json.dumps(_json_value(value), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
