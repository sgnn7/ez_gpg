import unittest

from ez_gpg.config import Config


class TestConfig(unittest.TestCase):
    def test_key_id_size(self):
        self.assertEqual(Config.KEY_ID_SIZE, 16)

    def test_keyservers_returns_list(self):
        servers = Config.get_keyservers()
        self.assertIsInstance(servers, list)
        self.assertTrue(len(servers) > 0)

    def test_keyservers_are_strings(self):
        for server in Config.get_keyservers():
            self.assertIsInstance(server, str)
            self.assertTrue(len(server) > 0)


if __name__ == '__main__':
    unittest.main()
