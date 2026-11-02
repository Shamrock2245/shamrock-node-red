#!/usr/bin/env python3
"""CI wrapper: entrypoint must survive an empty node_modules and a root-owned flows.json."""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class EntrypointBootTests(unittest.TestCase):
    def test_empty_node_modules_and_root_owned_flows(self) -> None:
        script = ROOT / "scripts" / "test_entrypoint_boot.sh"
        result = subprocess.run(
            ["bash", str(script)],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
