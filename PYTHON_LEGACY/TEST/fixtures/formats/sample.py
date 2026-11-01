"""
Edge Anomaly Detector Service.
Monitors node telemetry streams and flags statistical outliers.
"""

from dataclasses import dataclass
from typing import List, Optional
import math


@dataclass
class TelemetryRecord:
    timestamp: float
    voltage: float
    current: float
    vibration_amplitude: float


class AnomalyDetector:
    """Calculates rolling z-scores across multi-axis industrial sensor streams."""

    def __init__(self, threshold_sigma: float = 3.0) -> None:
        self.threshold_sigma = threshold_sigma
        self.history: List[float] = []

    def record_observation(self, record: TelemetryRecord) -> bool:
        magnitude = math.sqrt(record.voltage**2 + record.current**2 + record.vibration_amplitude**2)
        self.history.append(magnitude)
        if len(self.history) < 10:
            return False

        mean = sum(self.history) / len(self.history)
        variance = sum((x - mean) ** 2 for x in self.history) / len(self.history)
        std_dev = math.sqrt(variance) if variance > 0 else 1.0

        z_score = abs(magnitude - mean) / std_dev
        return z_score > self.threshold_sigma
