"""Mock Kivy modules before any test imports to avoid requiring a display."""

import sys
from unittest.mock import MagicMock

# Mock all Kivy modules that might be imported through the ez_gpg package
_kivy_modules = [
    'kivy',
    'kivy.app',
    'kivy.config',
    'kivy.core',
    'kivy.core.window',
    'kivy.graphics',
    'kivy.uix',
    'kivy.uix.boxlayout',
    'kivy.uix.button',
    'kivy.uix.checkbox',
    'kivy.uix.gridlayout',
    'kivy.uix.label',
    'kivy.uix.popup',
    'kivy.uix.screenmanager',
    'kivy.uix.scrollview',
    'kivy.uix.spinner',
    'kivy.uix.tabbedpanel',
    'kivy.uix.textinput',
    'kivy.uix.filechooser',
]

for mod in _kivy_modules:
    sys.modules[mod] = MagicMock()
