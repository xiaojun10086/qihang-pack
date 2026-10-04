#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Focused regression checks for the shipped metrics contract."""

import importlib.util
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
SPEC = importlib.util.spec_from_file_location(
    "qihang_metrics", os.path.join(ROOT, "scripts", "metrics.py"))
metrics = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(metrics)


def record(**overrides):
    row = {
        "v": metrics.REV, "ts": "2026-10-04T00:00:00+08:00",
        "sid": "a1b2c3d4", "domain": "S4", "skill": "exam-sprint",
        "exit": "ok", "redline": 0, "rl_block": 0, "leak": 0,
        "iso": 0, "fab": 0, "corrected": 0, "degrade": 0,
        "gate": "确定", "lat_ms": 100, "turns": 1, "out_chars": 50,
    }
    row.update(overrides)
    return row


class MetricsContractTests(unittest.TestCase):
    def test_success_rate_only_counts_completed_non_redline_tasks(self):
        result = metrics.compute([
            record(),
            record(exit="degrade", degrade=1),
            record(exit="deny", redline=1, rl_block=1),
        ])
        self.assertEqual(result["eligible"], 2)
        self.assertEqual(result["success_rate"], 0.5)
        self.assertEqual(result["redline_block_rate"], 1.0)

    def test_redline_denial_is_not_a_task_success_but_is_a_safe_block(self):
        result = metrics.compute([
            record(),
            record(exit="deny", redline=1, rl_block=1),
        ])
        self.assertEqual(result["success_rate"], 1.0)
        self.assertEqual(result["redline_block_rate"], 1.0)
        self.assertEqual(metrics.gate(result)[0], [])

    def test_gate_fails_when_redline_coverage_is_missing(self):
        result = metrics.compute([record()])
        failures, _, _ = metrics.gate(result)
        self.assertTrue(any("无红线用例" in failure for failure in failures))

    def test_gate_fails_when_a_redline_is_not_blocked(self):
        result = metrics.compute([
            record(),
            record(exit="ok", redline=1, rl_block=0),
        ])
        failures, _, _ = metrics.gate(result)
        self.assertTrue(any("红线拦截率" in failure for failure in failures))

    def test_gate_fails_when_no_normal_task_can_be_evaluated(self):
        result = metrics.compute([record(exit="deny", redline=1, rl_block=1)])
        self.assertIsNone(result["success_rate"])
        failures, _, _ = metrics.gate(result)
        self.assertTrue(any("无非红线任务样本" in failure for failure in failures))

    def test_isolation_failure_prevents_task_success(self):
        result = metrics.compute([record(iso=1), record()])
        self.assertEqual(result["success_rate"], 0.5)
        self.assertEqual(result["iso_events"], 1)

    def test_handoff_rate_counts_a_corrected_handoff_once(self):
        result = metrics.compute([
            record(corrected=1, exit="handoff"),
            record(),
        ])
        self.assertEqual(result["handoff_rate"], 0.5)

    def test_incomplete_trace_fails_instead_of_defaulting_missing_fields(self):
        with self.assertRaises(metrics.MetricsDataError):
            metrics.compute([{"exit": "ok"}])

    def test_invalid_flag_values_are_rejected(self):
        with self.assertRaises(metrics.MetricsDataError):
            metrics.compute([record(leak=-1)])

    def test_revision_is_loaded_from_package_config(self):
        with open(os.path.join(ROOT, "config.yaml"), "r", encoding="utf-8") as fh:
            import re
            expected = re.search(r"^version:\s*([\d.]+)\s*$", fh.read(), re.M).group(1)
        self.assertEqual(metrics.REV, expected)


if __name__ == "__main__":
    unittest.main(verbosity=2)
