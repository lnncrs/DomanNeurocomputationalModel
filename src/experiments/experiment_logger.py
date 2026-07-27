"""Persistência JSON/JSONL explícita para execuções experimentais"""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from enum import Enum
import json
from pathlib import Path
from typing import Mapping, TYPE_CHECKING

from .experiment_report import generate_experiment_report

if TYPE_CHECKING:
    from .experiment_runner import ExperimentIterationResult


def _json_value(value: object) -> object:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return _json_value(asdict(value))
    if isinstance(value, Mapping):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise TypeError(f"unsupported value for experimental JSON: {type(value).__name__}")


class ExperimentLogger:
    def __init__(
        self,
        run_directory: str | Path,
        metadata: Mapping[str, object],
    ) -> None:
        self.run_directory = Path(run_directory)
        self.run_directory.mkdir(parents=True, exist_ok=False)
        self.iterations_path = self.run_directory / "iterations.jsonl"
        self._write_json(self.run_directory / "metadata.json", metadata)

    def log_iteration(self, result: ExperimentIterationResult) -> None:
        with self.iterations_path.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(_json_value(result), ensure_ascii=False))
            stream.write("\n")

    def write_summary(self, summary: Mapping[str, object]) -> None:
        self._write_json(self.run_directory / "summary.json", summary)

    def write_report(self) -> Path:
        """Materializa a análise visual após JSON e JSONL estarem completos."""

        return generate_experiment_report(self.run_directory)

    @staticmethod
    def _write_json(path: Path, value: object) -> None:
        path.write_text(
            json.dumps(_json_value(value), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
