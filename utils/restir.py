"""Simplified ReSTIR reservoir and sample utilities.

This module provides basic building blocks for spatio-temporal
resampling similar to the technique described in NVIDIA's ReSTIR GI
paper. It is not a full implementation but offers the core data
structures required to experiment with reservoir-based sampling in
Python.
"""

from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Callable, Optional

import numpy as np


@dataclass
class Sample:
    """A shading sample representing a light path vertex."""

    position: np.ndarray  # world position of the sample point
    normal: np.ndarray    # surface normal at the sample point
    radiance: np.ndarray  # RGB radiance leaving the sample point
    pdf: float            # probability density used to generate the sample


class Reservoir:
    """Weighted reservoir for resampled importance sampling."""

    def __init__(self) -> None:
        self.sample: Optional[Sample] = None
        self.wsum: float = 0.0
        self.M: int = 0

    def update(self, candidate: Sample, weight: float) -> None:
        """Consider ``candidate`` for inclusion in the reservoir."""
        self.wsum += weight
        self.M += 1
        if random.random() < weight / self.wsum:
            self.sample = candidate

    def merge(self, other: "Reservoir", weight_func: Callable[[Sample], float]) -> None:
        """Merge another reservoir into this one."""
        if other.sample is None:
            return
        w = weight_func(other.sample) * other.wsum / max(1, other.M)
        self.update(other.sample, w)
        self.M += other.M

    def get_weight(self, target_func: Callable[[Sample], float]) -> float:
        """Return the RIS weight for the stored sample."""
        if self.sample is None:
            return 0.0
        return self.wsum / max(1, self.M) / target_func(self.sample)
