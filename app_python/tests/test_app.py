import os
import sys

import unittest
from unittest.mock import patch


# Allow importing app_python/app.py as a module named "app"
TESTS_DIR = os.path.dirname(__file__)
APP_DIR = os.path.dirname(TESTS_DIR)
sys.path.insert(0, APP_DIR)

import app as app_module  # noqa: E402


class DevOpsInfoServiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app_module.app.config.update(
            TESTING=False,
            PROPAGATE_EXCEPTIONS=False,
        )
        cls.client = app_module.app.test_client()

    def test_root_endpoint_returns_expected_structure_and_types(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.is_json)

        data = response.get_json()
        self.assertIsInstance(data, dict)

        for key in ("service", "system", "runtime", "request", "endpoints"):
            self.assertIn(key, data)

        self.assertEqual(data["service"]["name"], "devops-info-service")
        self.assertEqual(data["service"]["version"], "1.0.0")
        self.assertEqual(data["service"]["framework"], "Flask")
        self.assertIsInstance(data["service"]["description"], str)

        self.assertIsInstance(data["system"]["hostname"], str)
        self.assertIsInstance(data["system"]["platform"], str)
        self.assertIsInstance(data["system"]["platform_version"], str)
        self.assertIsInstance(data["system"]["architecture"], str)
        self.assertIsInstance(data["system"]["cpu_count"], int)
        self.assertIsInstance(data["system"]["python_version"], str)

        self.assertGreaterEqual(data["runtime"]["uptime_seconds"], 0)
        self.assertIsInstance(data["runtime"]["uptime_human"], str)
        self.assertIsInstance(data["runtime"]["current_time"], str)
        self.assertEqual(data["runtime"]["timezone"], "UTC")

        self.assertEqual(data["request"]["method"], "GET")
        self.assertEqual(data["request"]["path"], "/")
        self.assertIn("client_ip", data["request"])
        self.assertIsInstance(data["request"]["user_agent"], str)

        self.assertIsInstance(data["endpoints"], list)
        self.assertGreater(len(data["endpoints"]), 0)
        for endpoint in data["endpoints"]:
            self.assertIn("path", endpoint)
            self.assertIn("method", endpoint)
            self.assertIn("description", endpoint)

    def test_root_endpoint_extracts_forwarded_ip_and_user_agent(self):
        response = self.client.get(
            "/",
            headers={
                "X-Forwarded-For": "203.0.113.10",
                "User-Agent": "unit-test-agent/1.0",
            },
            environ_base={"REMOTE_ADDR": "127.0.0.1"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertEqual(data["request"]["client_ip"], "203.0.113.10")
        self.assertEqual(data["request"]["user_agent"], "unit-test-agent/1.0")

    def test_health_endpoint_returns_expected_payload(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.is_json)

        data = response.get_json()
        self.assertEqual(data["status"], "healthy")
        self.assertIsInstance(data["timestamp"], str)
        self.assertGreaterEqual(data["uptime_seconds"], 0)

    def test_not_found_returns_json_404(self):
        response = self.client.get("/does-not-exist")
        self.assertEqual(response.status_code, 404)
        self.assertTrue(response.is_json)

        data = response.get_json()
        self.assertEqual(data["error"], "Not Found")
        self.assertEqual(data["message"], "Endpoint does not exist")

    def test_root_returns_json_500_on_internal_error(self):
        with patch.object(
            app_module, "get_system_info", side_effect=RuntimeError("simulated failure")
        ):
            response = self.client.get("/")

        self.assertEqual(response.status_code, 500)
        self.assertTrue(response.is_json)
        self.assertEqual(
            response.get_json(),
            {
                "error": "Internal Server Error",
                "message": "An unexpected error occurred",
            },
        )

    def test_health_returns_json_500_on_internal_error(self):
        with patch.object(
            app_module, "get_uptime", side_effect=RuntimeError("simulated failure")
        ):
            response = self.client.get("/health")

        self.assertEqual(response.status_code, 500)
        self.assertTrue(response.is_json)
        self.assertEqual(
            response.get_json(),
            {
                "error": "Internal Server Error",
                "message": "An unexpected error occurred",
            },
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
