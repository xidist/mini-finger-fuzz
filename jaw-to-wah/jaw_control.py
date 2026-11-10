"""Timestamped jaw-to-wah control without external dependencies."""

import math


def _finite_number(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite number")
    try:
        value = float(value)
    except OverflowError as error:
        raise ValueError(f"{name} must be a finite number") from error
    if not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    return value


class JawControl:
    """Map calibrated jaw scores to a smoothed wah value in [0, 1]."""

    def __init__(self, closed, opened, smoothing_ms=60, neutral=0):
        self._closed = _finite_number(closed, "closed")
        self._opened = _finite_number(opened, "opened")
        if not 0 <= self._closed < self._opened <= 1:
            raise ValueError("calibration must satisfy 0 <= closed < opened <= 1")
        self._smoothing_ms = _finite_number(smoothing_ms, "smoothing_ms")
        if self._smoothing_ms < 0:
            raise ValueError("smoothing_ms must be nonnegative")
        self._neutral = _finite_number(neutral, "neutral")
        if not 0 <= self._neutral <= 1:
            raise ValueError("neutral must be in [0, 1]")
        self._last_ms = None
        self._output = self._neutral

    def update(self, timestamp_ms, jaw):
        """Process one sample. Use None when tracking is unavailable."""
        if type(timestamp_ms) is not int or not 0 <= timestamp_ms <= 2**63 - 1:
            raise ValueError("timestamp_ms must be a nonnegative signed 64-bit integer")
        if self._last_ms is not None and timestamp_ms <= self._last_ms:
            raise ValueError("timestamps must be strictly increasing")

        if jaw is None:
            target = self._neutral
        else:
            jaw = _finite_number(jaw, "jaw")
            jaw = min(self._opened, max(self._closed, jaw))
            target = (jaw - self._closed) / (self._opened - self._closed)

        if self._last_ms is None or self._smoothing_ms == 0:
            output = target
        else:
            elapsed_ms = timestamp_ms - self._last_ms
            alpha = -math.expm1(-elapsed_ms / self._smoothing_ms)
            output = self._output + alpha * (target - self._output)

        self._last_ms = timestamp_ms
        self._output = min(1.0, max(0.0, output))
        return self._output
