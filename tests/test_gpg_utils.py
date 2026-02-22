import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Mock gi and GTK before importing gpg_utils so tests run without GTK
gi_mock = MagicMock()
gi_mock.require_version = MagicMock()
sys.modules['gi'] = gi_mock
sys.modules['gi.repository'] = MagicMock()
sys.modules['gi.repository.Gtk'] = MagicMock()

from ez_gpg.gpg_utils import GpgUtils


class TestFindGpgBinary(unittest.TestCase):
    @patch('shutil.which')
    def test_finds_gpg_on_path(self, mock_which):
        mock_which.side_effect = lambda name: '/usr/bin/gpg' if name == 'gpg' else None
        result = GpgUtils._find_gpg_binary()
        self.assertEqual(result, '/usr/bin/gpg')

    @patch('shutil.which')
    def test_finds_gpg2_on_path(self, mock_which):
        mock_which.side_effect = lambda name: '/usr/bin/gpg2' if name == 'gpg2' else None
        result = GpgUtils._find_gpg_binary()
        self.assertEqual(result, '/usr/bin/gpg2')

    @patch('shutil.which')
    def test_prefers_gpg_over_gpg2(self, mock_which):
        mock_which.side_effect = lambda name: {
            'gpg': '/usr/bin/gpg',
            'gpg2': '/usr/bin/gpg2',
        }.get(name)
        result = GpgUtils._find_gpg_binary()
        self.assertEqual(result, '/usr/bin/gpg')

    @patch('shutil.which', return_value=None)
    @patch('sys.platform', 'darwin')
    @patch('os.path.isfile')
    @patch('os.access')
    def test_finds_homebrew_apple_silicon_gpg(self, mock_access, mock_isfile, mock_which):
        mock_isfile.side_effect = lambda path: path == '/opt/homebrew/bin/gpg'
        mock_access.return_value = True
        result = GpgUtils._find_gpg_binary()
        self.assertEqual(result, '/opt/homebrew/bin/gpg')

    @patch('shutil.which', return_value=None)
    @patch('sys.platform', 'darwin')
    @patch('os.path.isfile')
    @patch('os.access')
    def test_finds_homebrew_intel_gpg(self, mock_access, mock_isfile, mock_which):
        mock_isfile.side_effect = lambda path: path == '/usr/local/bin/gpg'
        mock_access.return_value = True
        result = GpgUtils._find_gpg_binary()
        self.assertEqual(result, '/usr/local/bin/gpg')

    @patch('shutil.which', return_value=None)
    @patch('sys.platform', 'darwin')
    @patch('os.path.isfile')
    @patch('os.access')
    def test_finds_gpg_suite_binary(self, mock_access, mock_isfile, mock_which):
        mock_isfile.side_effect = lambda path: path == '/usr/local/MacGPG2/bin/gpg2'
        mock_access.return_value = True
        result = GpgUtils._find_gpg_binary()
        self.assertEqual(result, '/usr/local/MacGPG2/bin/gpg2')

    @patch('shutil.which', return_value=None)
    @patch('sys.platform', 'darwin')
    @patch('os.path.isfile', return_value=False)
    def test_falls_back_to_gpg_on_macos(self, mock_isfile, mock_which):
        result = GpgUtils._find_gpg_binary()
        self.assertEqual(result, 'gpg')

    @patch('shutil.which', return_value=None)
    @patch('sys.platform', 'linux')
    def test_falls_back_to_gpg_on_linux(self, mock_which):
        result = GpgUtils._find_gpg_binary()
        self.assertEqual(result, 'gpg')


class TestGetGpgKeyring(unittest.TestCase):
    @patch('ez_gpg.gpg_utils.gnupg.GPG')
    @patch.object(GpgUtils, '_find_gpg_binary', return_value='/usr/local/bin/gpg')
    def test_passes_binary_to_gnupg(self, mock_find, mock_gpg_class):
        GpgUtils.get_gpg_keyring()
        mock_gpg_class.assert_called_once_with(gpgbinary='/usr/local/bin/gpg',
                                                     options=['--pinentry-mode', 'loopback'])


class TestCreateKey(unittest.TestCase):
    @patch('ez_gpg.gpg_utils.gnupg.GPG')
    @patch.object(GpgUtils, '_find_gpg_binary', return_value='/usr/bin/gpg')
    def test_create_key_returns_fingerprint_on_success(self, mock_find, mock_gpg_class):
        mock_gpg = MagicMock()
        mock_gpg_class.return_value = mock_gpg
        mock_gpg.gen_key_input.return_value = 'input_data'
        mock_key = MagicMock()
        mock_key.fingerprint = 'ABCD1234EFGH5678'
        mock_gpg.gen_key.return_value = mock_key

        result = GpgUtils.create_key('Test User', 'test@example.com', 'secret')
        self.assertEqual(result, 'ABCD1234EFGH5678')

        mock_gpg.gen_key_input.assert_called_once_with(
            key_type='RSA',
            key_length=4096,
            name_real='Test User',
            name_email='test@example.com',
            passphrase='secret',
        )
        mock_gpg.gen_key.assert_called_once_with('input_data')

    @patch('ez_gpg.gpg_utils.gnupg.GPG')
    @patch.object(GpgUtils, '_find_gpg_binary', return_value='/usr/bin/gpg')
    def test_create_key_returns_none_on_failure(self, mock_find, mock_gpg_class):
        mock_gpg = MagicMock()
        mock_gpg_class.return_value = mock_gpg
        mock_gpg.gen_key_input.return_value = 'input_data'
        mock_key = MagicMock()
        mock_key.fingerprint = ''
        mock_gpg.gen_key.return_value = mock_key

        result = GpgUtils.create_key('Test User', 'test@example.com', 'secret')
        self.assertIsNone(result)

    @patch('ez_gpg.gpg_utils.gnupg.GPG')
    @patch.object(GpgUtils, '_find_gpg_binary', return_value='/usr/bin/gpg')
    def test_create_key_passes_custom_key_type_and_length(self, mock_find, mock_gpg_class):
        mock_gpg = MagicMock()
        mock_gpg_class.return_value = mock_gpg
        mock_gpg.gen_key_input.return_value = 'input_data'
        mock_key = MagicMock()
        mock_key.fingerprint = 'FINGERPRINT123'
        mock_gpg.gen_key.return_value = mock_key

        result = GpgUtils.create_key('User', 'u@e.com', 'pass', key_type='DSA', key_length=2048)
        self.assertEqual(result, 'FINGERPRINT123')

        mock_gpg.gen_key_input.assert_called_once_with(
            key_type='DSA',
            key_length=2048,
            name_real='User',
            name_email='u@e.com',
            passphrase='pass',
        )


if __name__ == '__main__':
    unittest.main()
