"""Regression checks for the public repository's privacy boundary."""
import importlib.util
import unittest
from pathlib import Path
spec = importlib.util.spec_from_file_location('privacy', Path(__file__).resolve().parents[1] / 'scripts/check_public_privacy.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class PrivacyTests(unittest.TestCase):
    def test_runtime_paths(self):
        for path in ['workspaces/tencent-docs-api/.env', 'workspaces/tencent-docs-api/token_cache.json', 'workspaces/order-shipment/browser-profile/Default/Cookies', 'workspaces/order-shipment/TMP/result.json', 'workspaces/order-shipment/attachments/example.pdf', 'workspaces/medical-inventory-tencent-import/artifacts/verification/check.json']:
            self.assertTrue(m.violations(path, b'{}'), path)
    def test_placeholder_docs(self):
        self.assertFalse(m.violations('workspaces/tencent-docs-api/README.md', b'ACCESS_TOKEN=<your_access_token>'))
    def test_sensitive_patterns(self):
        for value in [b'/Users/' + b'example/private/file', b'ghp_' + b'a'*30, b'user' + b'@gmail.com']:
            self.assertTrue(m.violations('example.txt', value))

if __name__ == '__main__':
    unittest.main()
