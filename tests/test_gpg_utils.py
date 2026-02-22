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
        mock_gpg_class.assert_called_once_with(gpgbinary='/usr/local/bin/gpg')


if __name__ == '__main__':
    unittest.main()
