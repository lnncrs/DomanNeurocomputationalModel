"""Conversão das observações experimentais em entradas para a rede neural."""

from __future__ import annotations

from dataclasses import dataclass
import math

from src.neural import SensoryInput


@dataclass(frozen=True)
class SensoryObservation:
    """
    Valores observados antes da normalização experimental.

    As unidades e a forma de obtenção pertencem ao experimento: por exemplo,
    aceleração derivada dos sensores do Webots, frequência de transições
    visuais e intensidade do evento sonoro.
    """

    acceleration: float = 0.0
    visual: float = 0.0
    sound: float = 0.0

    def __post_init__(self) -> None:
        if not all(
            math.isfinite(value)
            for value in (self.acceleration, self.visual, self.sound)
        ):
            raise ValueError("sensory observations must be finite")


@dataclass(frozen=True)
class SensoryNormalization:
    """
    Transformação linear adotada para os três canais experimentais.

    Esta normalização é uma adaptação necessária para integrar grandezas
    físicas distintas; ela não faz parte da dinâmica neural descrita no
    artigo.
    """

    acceleration_offset: float = 0.0
    acceleration_scale: float = 1.0
    visual_offset: float = 0.0
    visual_scale: float = 1.0
    sound_offset: float = 0.0
    sound_scale: float = 1.0

    def __post_init__(self) -> None:
        values = (
            self.acceleration_offset,
            self.acceleration_scale,
            self.visual_offset,
            self.visual_scale,
            self.sound_offset,
            self.sound_scale,
        )
        if not all(math.isfinite(value) for value in values):
            raise ValueError("sensory normalization parameters must be finite")


class SensoryProcessor:
    """
    Prepara estímulos escalares sem expor grandezas físicas à rede neural.

    O processador é a fronteira entre o protocolo experimental e
    ``FourNeuronNetwork``. A rede recebe somente o ``SensoryInput`` resultante.
    """

    def __init__(self, normalization: SensoryNormalization | None = None) -> None:
        self.normalization = normalization or SensoryNormalization()

    def process(self, observation: SensoryObservation) -> SensoryInput:
        """Aplica a normalização experimental aos três canais observados."""

        normalization = self.normalization
        return SensoryInput(
            acceleration=(
                observation.acceleration - normalization.acceleration_offset
            )
            * normalization.acceleration_scale,
            visual=(observation.visual - normalization.visual_offset)
            * normalization.visual_scale,
            sound=(observation.sound - normalization.sound_offset)
            * normalization.sound_scale,
        )
