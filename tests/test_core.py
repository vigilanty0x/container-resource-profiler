import unittest
from container_resource_profiler import evaluate

GOOD = {"scenario":"startup","cpu_percent":32.5,"memory_mb":128,"io_mb":2,"network_mb":1,"startup_ms":900}
BAD = {"scenario":"startup","cpu_percent":True,"memory_mb":True,"io_mb":True,"network_mb":True,"startup_ms":True}

class ContractTests(unittest.TestCase):
    def test_valid_record_builds_domain_artifact(self):
        result = evaluate(GOOD)
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["profile"]["cpu_percent"], 32.5)
        self.assertEqual(len(result["evidence_sha256"]), 64)

    def test_result_is_deterministic(self):
        self.assertEqual(evaluate(GOOD), evaluate(dict(reversed(list(GOOD.items())))))

    def test_semantic_counterexample_fails_closed(self):
        self.assertEqual(evaluate(BAD)["status"], "failed")

    def test_missing_field_blocks(self):
        record = dict(GOOD)
        record.pop(next(iter(record)))
        self.assertEqual(evaluate(record)["status"], "blocked")

    def test_boolean_numeric_spoof_is_rejected_when_present(self):
        record = dict(GOOD)
        numeric = next((key for key in ("default_status", "duration_ms", "completed", "tests_passed", "cpu_percent", "tests_total") if key in record), None)
        if numeric is None:
            self.skipTest("no numeric contract")
        record[numeric] = True
        self.assertEqual(evaluate(record)["status"], "failed")

if __name__ == "__main__":
    unittest.main()

