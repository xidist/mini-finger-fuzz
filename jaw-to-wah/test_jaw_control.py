"""Behavior checks for the pure-Python controller."""

import math
import unittest

from jaw_control import JawControl


class JawControlTests(unittest.TestCase):
    def test_calibration_endpoints_and_midpoint(self):
        control = JawControl(0.25, 0.75, smoothing_ms=0)
        self.assertEqual(control.update(0, 0.25), 0)
        self.assertEqual(control.update(10, 0.5), 0.5)
        self.assertEqual(control.update(20, 0.75), 1)

    def test_out_of_range_values_clamp(self):
        control = JawControl(0.25, 0.75, smoothing_ms=0)
        for timestamp, (jaw, expected) in enumerate(
            [(-10, 0), (0.1, 0), (0.9, 1), (10, 1)]
        ):
            with self.subTest(jaw=jaw):
                self.assertEqual(control.update(timestamp, jaw), expected)

    def test_invalid_configuration(self):
        for options in [
            (0.5, 0.5), (0.8, 0.2), (-0.1, 1), (0, 1.1),
            (0, 1, -1), (0, 1, 60, 2), (0, math.nan),
        ]:
            with self.subTest(options=options), self.assertRaises(ValueError):
                JawControl(*options)

    def test_smoothing_matches_elapsed_time(self):
        direct = JawControl(0, 1, smoothing_ms=100)
        stepped = JawControl(0, 1, smoothing_ms=100)
        self.assertEqual(direct.update(0, 0), 0)
        stepped.update(0, 0)
        stepped.update(25, 1)
        expected = 1 - math.exp(-1)
        self.assertAlmostEqual(direct.update(100, 1), expected)
        self.assertAlmostEqual(stepped.update(100, 1), expected)

    def test_missing_tracking_drifts_to_neutral_and_recovers(self):
        control = JawControl(0, 1, smoothing_ms=100, neutral=0.2)
        self.assertEqual(control.update(0, None), 0.2)
        self.assertAlmostEqual(control.update(100, 1), 1 - 0.8 / math.e)
        previous = control.update(200, None)
        self.assertAlmostEqual(previous, 0.2 + 0.8 * (1 - 1 / math.e) / math.e)
        self.assertAlmostEqual(control.update(5000, None), 0.2)
        self.assertAlmostEqual(control.update(5100, 1), 1 - 0.8 / math.e)

    def test_missing_tracking_without_smoothing(self):
        control = JawControl(0, 1, smoothing_ms=0, neutral=0.3)
        self.assertEqual(control.update(0, 1), 1)
        self.assertEqual(control.update(10, None), 0.3)

    def test_malformed_and_non_monotonic_timestamps(self):
        control = JawControl(0, 1, smoothing_ms=100)
        control.update(10, 0)
        for timestamp in (-1, 2**63, 10, 9, 20.0, "20", True, None, math.nan, math.inf):
            with self.subTest(timestamp=timestamp), self.assertRaises(ValueError):
                control.update(timestamp, 1)
        self.assertAlmostEqual(control.update(110, 1), 1 - 1 / math.e)

    def test_malformed_scores_leave_state_unchanged(self):
        control = JawControl(0, 1, smoothing_ms=100)
        control.update(0, 0)
        for jaw in ("0.5", True, math.nan, math.inf, -math.inf):
            with self.subTest(jaw=jaw), self.assertRaises(ValueError):
                control.update(100, jaw)
        self.assertAlmostEqual(control.update(100, 1), 1 - 1 / math.e)


if __name__ == "__main__":
    unittest.main()
