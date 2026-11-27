#!/usr/bin/python3
import sys
import unittest

sys.path.append("..")
sys.path.append("../core")

from framework.lib.time.time_helper import time_remaining


class TestTimeRemaining(unittest.TestCase):
    CASES: list[tuple[int, str]] = [
        (0, "0sec"),
        (1, "1sec"),
        (59, "59sec"),
        (60, "1min"),
        (61, "1min 1sec"),
        (3599, "59min 59sec"),
        (3600, "1h"),
        (3601, "1h 1sec"),
        (3661, "1h 1min 1sec"),
        (5420, "1h 30min 20sec"),
        (86399, "23h 59min 59sec"),
        (86400, "1d"),
        (90001, "1d 1h 1sec"),
        (90061, "1d 1h 1min 1sec"),
        (604800, "7d"),
    ]

    def test_cases(self) -> None:
        for duration, expected in self.CASES:
            with self.subTest(duration=duration):
                self.assertEqual(time_remaining(duration), expected)

    def test_returns_string(self) -> None:
        self.assertIsInstance(time_remaining(42), str)


def main() -> None:
    unittest.main()


if __name__ == "__main__":
    main()