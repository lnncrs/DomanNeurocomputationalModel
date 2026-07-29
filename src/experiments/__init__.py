"""Protocolo e persistência dos experimentos de aprendizagem"""

from .experiment_logger import ExperimentLogger
from .experiment_report import generate_experiment_report
from .experiment_runner import (
    ExperimentConfig,
    ExperimentIterationResult,
    ExperimentRunner,
    LearningCriterion,
    LearningStatus,
    MovementDirection,
)
from .sensory_processing import (
    SensoryNormalization,
    SensoryObservation,
    SensoryProcessor,
)

__all__ = [
    "ExperimentConfig",
    "ExperimentIterationResult",
    "ExperimentLogger",
    "ExperimentRunner",
    "generate_experiment_report",
    "LearningCriterion",
    "LearningStatus",
    "MovementDirection",
    "SensoryNormalization",
    "SensoryObservation",
    "SensoryProcessor",
]
