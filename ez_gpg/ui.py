# vim:ff=unix ts=4 sw=4 expandtab

import os
import re

from kivy.config import Config as KivyConfig
KivyConfig.set('input', 'mouse', 'mouse,multitouch_on_demand')

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.spinner import Spinner as KivySpinner
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from .config import Config
from .gpg_utils import GpgUtils
from .ui_utils import UiUtils


class BaseScreen(Screen):
    """Base screen with common functionality."""
    _window_size = (700, 500)
    _back_target = 'main'

    def _go_back(self, instance=None):
        self.manager.transition = NoTransition()
        self.manager.current = self._back_target

    def _show_error_message(self, message):
        print(f"ERROR! {message}")
        UiUtils.show_dialog(None, message)

    def on_enter(self):
        Window.size = self._window_size

    def on_pre_enter(self):
        pass


class MainScreen(BaseScreen):
    _window_size = (280, 100)

    def __init__(self, **kwargs):
        super().__init__(name='main', **kwargs)

        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)

        # 2x2 grid: Encrypt/Decrypt, Sign/Verify
        grid = GridLayout(cols=2, spacing=10, size_hint_y=None)
        for text, target in [
            ('Encrypt', 'encrypt'),
            ('Decrypt', 'decrypt'),
            ('Sign', 'sign'),
            ('Verify', 'verify'),
        ]:
            btn = Button(text=text, font_size='14sp')
            btn.screen_target = target
            btn.bind(on_release=self._navigate)
            grid.add_widget(btn)
        layout.add_widget(grid)

        # Key Management spanning full width
        km_btn = Button(text='Key Management', size_hint_y=None, height=40,
                        font_size='14sp')
        km_btn.screen_target = 'key_management'
        km_btn.bind(on_release=self._navigate)
        layout.add_widget(km_btn)

        self.add_widget(layout)

    def on_enter(self):
        super().on_enter()
        App.get_running_app().title = 'EZ GPG \u2013 Home'

    def _navigate(self, instance):
        print(f"Clicked {instance.text} button")
        self.manager.transition = NoTransition()
        self.manager.current = instance.screen_target


class EncryptScreen(BaseScreen):
    _window_size = (680, 600)

    def __init__(self, **kwargs):
        super().__init__(name='encrypt', **kwargs)

        layout = BoxLayout(orientation='vertical', padding=10, spacing=6)

        # Embedded file chooser (top portion)
        self._file_chooser = FileChooserListView(
            multiselect=True,
            path=os.path.expanduser('~'),
            size_hint_y=0.55)
        layout.add_widget(self._file_chooser)

        # Tabbed panel: Public Key / Symetric Key
        self._tab_panel = TabbedPanel(do_default_tab=False, tab_width=150,
                                      size_hint_y=0.38)

        # PKI Tab
        pki_tab = TabbedPanelItem(text='Public Key')
        self._key_scroll = ScrollView()
        self._key_list_layout = BoxLayout(orientation='vertical',
                                          size_hint_y=None, spacing=4, padding=4)
        self._key_list_layout.bind(
            minimum_height=self._key_list_layout.setter('height'))
        self._key_scroll.add_widget(self._key_list_layout)
        pki_tab.add_widget(self._key_scroll)
        self._tab_panel.add_widget(pki_tab)

        # Symmetric Tab
        sym_tab = TabbedPanelItem(text='Symetric Key')
        sym_layout = BoxLayout(orientation='vertical', padding=10, spacing=8)

        pw_row = BoxLayout(size_hint_y=None, height=36, spacing=10)
        pw_row.add_widget(Label(text='Password:', size_hint_x=None, width=130,
                                halign='right', valign='middle',
                                text_size=(130, 36)))
        self._password_field = TextInput(password=True, multiline=False)
        pw_row.add_widget(self._password_field)
        sym_layout.add_widget(pw_row)

        cpw_row = BoxLayout(size_hint_y=None, height=36, spacing=10)
        cpw_row.add_widget(Label(text='Confirm Password:', size_hint_x=None,
                                 width=130, halign='right', valign='middle',
                                 text_size=(130, 36)))
        self._confirm_password_field = TextInput(password=True, multiline=False)
        cpw_row.add_widget(self._confirm_password_field)
        sym_layout.add_widget(cpw_row)

        sym_layout.add_widget(BoxLayout())  # spacer
        sym_tab.add_widget(sym_layout)
        self._tab_panel.add_widget(sym_tab)

        layout.add_widget(self._tab_panel)

        # Bottom row with Encrypt button right-aligned
        btn_row = BoxLayout(size_hint_y=None, height=36)
        btn_row.add_widget(BoxLayout())  # left spacer
        self._encrypt_btn = Button(text='Encrypt', size_hint_x=None, width=100,
                                   font_size='14sp')
        self._encrypt_btn.bind(on_release=self._do_encrypt)
        btn_row.add_widget(self._encrypt_btn)
        layout.add_widget(btn_row)

        self.add_widget(layout)

    def on_enter(self):
        super().on_enter()
        App.get_running_app().title = 'EZ GPG - Encrypt'

    def on_pre_enter(self):
        self._password_field.text = ''
        self._confirm_password_field.text = ''
        self._encrypt_btn.disabled = False
        self._file_chooser.selection = []
        self._populate_key_list()

    def _populate_key_list(self):
        self._key_list_layout.clear_widgets()
        self._key_checkboxes = []

        for key in GpgUtils.get_gpg_keys():
            key_id = key[0]
            key_friendly_name = key[2]

            row = BoxLayout(size_hint_y=None, height=28)
            cb = CheckBox(size_hint_x=None, width=28)
            cb.key_id = key_id
            row.add_widget(cb)
            row.add_widget(Label(text=key_friendly_name, halign='left',
                                 text_size=(500, None), font_size='13sp'))

            self._key_checkboxes.append(cb)
            self._key_list_layout.add_widget(row)

    def _do_encrypt(self, instance):
        print("Clicked Encrypt Content button")

        filenames = self._file_chooser.selection
        if not filenames:
            self._show_error_message("File not selected!")
            return

        current_tab = self._tab_panel.current_tab
        is_pki = current_tab.text.startswith('Public')

        if is_pki:
            self._encrypt_pki(filenames)
        else:
            self._encrypt_symmetric(filenames)

    def _encrypt_pki(self, filenames):
        selected_keys = [cb.key_id for cb in self._key_checkboxes if cb.active]

        if not selected_keys:
            self._show_error_message("No key selected!")
            return

        self._encrypt_btn.disabled = True
        GpgUtils.encrypt_files_pki(None, filenames, selected_keys, True)
        self._go_back()

    def _encrypt_symmetric(self, filenames):
        password = self._password_field.text
        confirmed = self._confirm_password_field.text

        if not password:
            self._show_error_message("No password set!")
            return

        if password != confirmed:
            self._show_error_message("Passwords do not match!")
            return

        self._encrypt_btn.disabled = True
        GpgUtils.encrypt_files_symmetric(None, filenames, password, True)
        self._go_back()


class DecryptScreen(BaseScreen):
    _window_size = (460, 220)

    def __init__(self, **kwargs):
        super().__init__(name='decrypt', **kwargs)

        self._source_file = None
        self._gpg_keys = []
        self._key_map = {}

        layout = BoxLayout(orientation='vertical', padding=15, spacing=8)

        # File chooser button (filename display + browse icon)
        file_row = BoxLayout(size_hint_y=None, height=36, spacing=2)
        self._file_display = TextInput(text='', readonly=True, multiline=False,
                                       hint_text='(no file selected)',
                                       font_size='13sp')
        file_row.add_widget(self._file_display)
        browse_btn = Button(text='\u2026', size_hint_x=None, width=36,
                            font_size='16sp')
        browse_btn.bind(on_release=self._select_file)
        file_row.add_widget(browse_btn)
        layout.add_widget(file_row)

        # Key dropdown (full width)
        self._key_spinner = KivySpinner(text='', values=[],
                                        size_hint_y=None, height=36,
                                        font_size='13sp')
        layout.add_widget(self._key_spinner)

        # Password field (full width)
        self._password_field = TextInput(password=True, multiline=False,
                                         size_hint_y=None, height=36,
                                         font_size='13sp')
        layout.add_widget(self._password_field)

        # Bottom row with Decrypt button right-aligned
        btn_row = BoxLayout(size_hint_y=None, height=36)
        btn_row.add_widget(BoxLayout())  # left spacer
        self._decrypt_btn = Button(text='Decrypt', size_hint_x=None, width=100,
                                   font_size='14sp')
        self._decrypt_btn.bind(on_release=self._do_decrypt)
        btn_row.add_widget(self._decrypt_btn)
        layout.add_widget(btn_row)

        self.add_widget(layout)

    def on_enter(self):
        super().on_enter()
        App.get_running_app().title = 'EZ GPG \u2013 Decrypt file'

    def on_pre_enter(self):
        self._source_file = None
        self._file_display.text = ''
        self._password_field.text = ''
        self._decrypt_btn.disabled = False
        self._populate_keys()

    def _populate_keys(self):
        self._gpg_keys = GpgUtils.get_gpg_keys(True)
        self._key_map = {}

        values = []
        for key in self._gpg_keys:
            key_id, key_name, key_friendly_name, subkeys, fingerprint = key
            self._key_map[key_friendly_name] = key_id
            values.append(key_friendly_name)

        values.append('Symmetric encryption (password only)')
        self._key_map['Symmetric encryption (password only)'] = 'symmetric'

        self._key_spinner.values = values
        self._key_spinner.text = values[0] if values else ''

    def _select_file(self, instance):
        filename = UiUtils.get_filename(title="Select file to decrypt")
        if filename:
            self._source_file = filename
            self._file_display.text = os.path.basename(filename)
            self._update_key_list()

    def _update_key_list(self):
        if not self._source_file:
            return

        info = GpgUtils.get_encryped_file_info(None, self._source_file)
        if not info:
            return

        if info.is_symmetric:
            print("Symmetric encryption")
            self._key_spinner.text = 'Symmetric encryption (password only)'
        else:
            print("Keys: ", info.key_ids)
            for key in self._gpg_keys:
                key_id, key_name, key_friendly_name, subkeys, fingerprint = key
                all_key_ids = [key_id, fingerprint] + subkeys
                for candidate in all_key_ids:
                    for enc_key in info.key_ids:
                        if candidate.endswith(enc_key) or enc_key.endswith(candidate):
                            print("Found! Matching key:", key_id, key_name)
                            self._key_spinner.text = key_friendly_name
                            return

            UiUtils.show_dialog(None,
                                "ERROR! You do not have a key that can decrypt this file!",
                                title="Missing decryption key")

    def _do_decrypt(self, instance):
        print("Clicked Decrypt button")

        if not self._source_file:
            self._show_error_message("File not selected!")
            return

        self._decrypt_btn.disabled = True

        success = GpgUtils.decrypt_file(None, self._source_file,
                                        self._password_field.text)

        if success:
            self._go_back()
        else:
            self._decrypt_btn.disabled = False


class SignScreen(BaseScreen):
    _window_size = (500, 220)

    def __init__(self, **kwargs):
        super().__init__(name='sign', **kwargs)

        self._source_file = None
        self._key_map = {}

        layout = BoxLayout(orientation='vertical', padding=15, spacing=8)

        # File chooser button
        file_row = BoxLayout(size_hint_y=None, height=36, spacing=2)
        self._file_display = TextInput(text='', readonly=True, multiline=False,
                                       hint_text='(no file selected)',
                                       font_size='13sp')
        file_row.add_widget(self._file_display)
        browse_btn = Button(text='\u2026', size_hint_x=None, width=36,
                            font_size='16sp')
        browse_btn.bind(on_release=self._select_file)
        file_row.add_widget(browse_btn)
        layout.add_widget(file_row)

        # Key dropdown
        self._key_spinner = KivySpinner(text='', values=[],
                                        size_hint_y=None, height=36,
                                        font_size='13sp')
        layout.add_widget(self._key_spinner)

        # Password field
        self._password_field = TextInput(password=True, multiline=False,
                                         size_hint_y=None, height=36,
                                         font_size='13sp')
        layout.add_widget(self._password_field)

        # Bottom row with Sign button right-aligned
        btn_row = BoxLayout(size_hint_y=None, height=36)
        btn_row.add_widget(BoxLayout())
        self._sign_btn = Button(text='Sign', size_hint_x=None, width=100,
                                font_size='14sp')
        self._sign_btn.bind(on_release=self._do_sign)
        btn_row.add_widget(self._sign_btn)
        layout.add_widget(btn_row)

        self.add_widget(layout)

    def on_enter(self):
        super().on_enter()
        App.get_running_app().title = 'EZ GPG \u2013 Sign file'

    def on_pre_enter(self):
        self._source_file = None
        self._file_display.text = ''
        self._password_field.text = ''
        self._sign_btn.disabled = False
        self._populate_keys()

    def _populate_keys(self):
        self._key_map = {}
        values = []
        for key in GpgUtils.get_gpg_keys(True):
            key_id, key_name, key_friendly_name, subkeys, fingerprint = key
            self._key_map[key_friendly_name] = key_id
            values.append(key_friendly_name)

        self._key_spinner.values = values
        self._key_spinner.text = values[0] if values else ''

    def _select_file(self, instance):
        filename = UiUtils.get_filename(title="Select file to sign")
        if filename:
            self._source_file = filename
            self._file_display.text = os.path.basename(filename)

    def _do_sign(self, instance):
        print("Clicked Sign button")

        if not self._source_file:
            self._show_error_message("File not selected!")
            return

        selected_text = self._key_spinner.text
        selected_key = self._key_map.get(selected_text)

        if not selected_key:
            self._show_error_message("No key selected!")
            return

        print(" - Key Id:", selected_key)

        self._sign_btn.disabled = True

        success = GpgUtils.sign_file(None, self._source_file, selected_key,
                                     self._password_field.text)

        if success:
            self._go_back()
        else:
            self._sign_btn.disabled = False


class VerifyScreen(BaseScreen):
    _window_size = (460, 200)

    def __init__(self, **kwargs):
        super().__init__(name='verify', **kwargs)

        self._source_file = None
        self._signature_file = None

        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)

        # Data File row
        data_row = BoxLayout(size_hint_y=None, height=36, spacing=8)
        data_row.add_widget(Label(text='Data File:', size_hint_x=None, width=80,
                                  halign='right', valign='middle',
                                  text_size=(80, 36), font_size='13sp'))
        self._file_display = TextInput(text='', readonly=True, multiline=False,
                                       hint_text='(none)', font_size='13sp')
        data_row.add_widget(self._file_display)
        data_browse = Button(text='\u2026', size_hint_x=None, width=36,
                             font_size='16sp')
        data_browse.bind(on_release=self._select_file)
        data_row.add_widget(data_browse)
        layout.add_widget(data_row)

        # Signature row
        sig_row = BoxLayout(size_hint_y=None, height=36, spacing=8)
        sig_row.add_widget(Label(text='Signature:', size_hint_x=None, width=80,
                                 halign='right', valign='middle',
                                 text_size=(80, 36), font_size='13sp'))
        self._sig_display = TextInput(text='', readonly=True, multiline=False,
                                      hint_text='(none)', font_size='13sp')
        sig_row.add_widget(self._sig_display)
        sig_browse = Button(text='\u2026', size_hint_x=None, width=36,
                            font_size='16sp')
        sig_browse.bind(on_release=self._select_signature)
        sig_row.add_widget(sig_browse)
        layout.add_widget(sig_row)

        # Spacer
        layout.add_widget(BoxLayout())

        # Verify button centered
        btn_row = BoxLayout(size_hint_y=None, height=36)
        btn_row.add_widget(BoxLayout())
        self._verify_btn = Button(text='Verify', size_hint_x=None, width=100,
                                  font_size='14sp')
        self._verify_btn.bind(on_release=self._do_verify)
        btn_row.add_widget(self._verify_btn)
        btn_row.add_widget(BoxLayout())
        layout.add_widget(btn_row)

        self.add_widget(layout)

    def on_enter(self):
        super().on_enter()
        App.get_running_app().title = 'EZ GPG \u2013 Verify Signature'

    def on_pre_enter(self):
        self._source_file = None
        self._signature_file = None
        self._file_display.text = ''
        self._sig_display.text = ''
        self._verify_btn.disabled = False

    def _select_file(self, instance):
        filename = UiUtils.get_filename(title="Select data file")
        if filename:
            self._source_file = filename
            self._file_display.text = os.path.basename(filename)

    def _select_signature(self, instance):
        filename = UiUtils.get_filename(title="Select signature file")
        if filename:
            self._signature_file = filename
            self._sig_display.text = os.path.basename(filename)

    def _do_verify(self, instance):
        print("Clicked Verify Signature button")

        if not self._source_file:
            self._show_error_message("File not selected!")
            return

        self._verify_btn.disabled = True

        success = GpgUtils.verify_file(None, self._source_file, self._signature_file)

        if success:
            self._go_back()
        else:
            self._verify_btn.disabled = False


class KeyManagementScreen(BaseScreen):
    _window_size = (600, 400)

    def __init__(self, **kwargs):
        super().__init__(name='key_management', **kwargs)

        self._selected_keys = []

        layout = BoxLayout(orientation='vertical', padding=10, spacing=6)

        # Toolbar matching screenshot: + Add, Import, Edit, Fetch, Upload, Export, Delete
        toolbar = BoxLayout(size_hint_y=None, height=36, spacing=4)

        self._create_btn = Button(text='+ Add', font_size='13sp')
        self._create_btn.bind(on_release=self._create_keys)
        toolbar.add_widget(self._create_btn)

        self._import_btn = Button(text='Import', font_size='13sp')
        self._import_btn.bind(on_release=self._import_keys)
        toolbar.add_widget(self._import_btn)

        self._edit_btn = Button(text='Edit', font_size='13sp', disabled=True)
        self._edit_btn.bind(on_release=self._edit_keys)
        toolbar.add_widget(self._edit_btn)

        self._fetch_btn = Button(text='Fetch', font_size='13sp')
        self._fetch_btn.bind(on_release=self._fetch_keys)
        toolbar.add_widget(self._fetch_btn)

        self._upload_btn = Button(text='Upload', font_size='13sp', disabled=True)
        self._upload_btn.bind(on_release=self._upload_keys)
        toolbar.add_widget(self._upload_btn)

        self._export_btn = Button(text='Export', font_size='13sp', disabled=True)
        self._export_btn.bind(on_release=self._export_keys)
        toolbar.add_widget(self._export_btn)

        self._delete_btn = Button(text='Delete', font_size='13sp', disabled=True,
)
        self._delete_btn.bind(on_release=self._delete_keys)
        toolbar.add_widget(self._delete_btn)

        layout.add_widget(toolbar)

        # Scrollable key list with checkboxes
        self._key_scroll = ScrollView()
        self._key_list_layout = BoxLayout(orientation='vertical',
                                          size_hint_y=None, spacing=2, padding=2)
        self._key_list_layout.bind(
            minimum_height=self._key_list_layout.setter('height'))
        self._key_scroll.add_widget(self._key_list_layout)
        layout.add_widget(self._key_scroll)

        self.add_widget(layout)

    def on_enter(self):
        super().on_enter()
        App.get_running_app().title = 'EZ GPG - Key Management'

    def on_pre_enter(self):
        self._selected_keys = []
        self._refresh_key_list()

    def _refresh_key_list(self):
        self._key_list_layout.clear_widgets()
        self._key_checkboxes = []
        self._selected_keys = []

        for key in GpgUtils.get_gpg_keys():
            key_id = key[0]
            key_friendly_name = key[2]

            row = BoxLayout(size_hint_y=None, height=28)
            cb = CheckBox(size_hint_x=None, width=28)
            cb.key_id = key_id
            cb.bind(active=self._on_key_toggled)
            row.add_widget(cb)
            row.add_widget(Label(text=key_friendly_name, halign='left',
                                 text_size=(500, None), font_size='13sp'))

            self._key_checkboxes.append(cb)
            self._key_list_layout.add_widget(row)

        self._update_button_state()

    def _on_key_toggled(self, checkbox, value):
        key_id = checkbox.key_id
        if value:
            if key_id not in self._selected_keys:
                self._selected_keys.append(key_id)
        else:
            self._selected_keys = [k for k in self._selected_keys if k != key_id]

        print("New selection list:")
        for key in self._selected_keys:
            print("Key:", key[-Config.KEY_ID_SIZE:])

        self._update_button_state()

    def _update_button_state(self):
        self._edit_btn.disabled = len(self._selected_keys) != 1
        self._export_btn.disabled = len(self._selected_keys) != 1
        self._upload_btn.disabled = len(self._selected_keys) == 0
        self._delete_btn.disabled = len(self._selected_keys) == 0

    def _create_keys(self, instance):
        print("Create Keys pressed...")
        self.manager.transition = NoTransition()
        self.manager.current = 'create_key'

    def _import_keys(self, instance):
        print("Import Keys pressed...")
        filename = UiUtils.get_filename(title="Import key file")
        if filename:
            print("Chosen file to import:", filename)
            if GpgUtils.import_key(filename):
                self._refresh_key_list()
            else:
                UiUtils.show_dialog(None,
                                    "ERROR! Keyfile could not be imported",
                                    title="Keyfile error")

    def _edit_keys(self, instance):
        print("Edit Keys pressed...")
        UiUtils.show_unimplemented_message_box()

    def _fetch_keys(self, instance):
        print("Fetch Keys pressed...")

        content = BoxLayout(orientation='vertical', padding=10, spacing=10)

        ks_row = BoxLayout(size_hint_y=None, height=34, spacing=8)
        ks_row.add_widget(Label(text='Keyserver:', size_hint_x=None, width=80,
                                halign='right', valign='middle',
                                text_size=(80, 34), font_size='13sp'))
        keyservers = Config.get_keyservers()
        ks_spinner = KivySpinner(text=keyservers[0], values=keyservers,
                                 font_size='12sp')
        ks_row.add_widget(ks_spinner)
        content.add_widget(ks_row)

        id_row = BoxLayout(size_hint_y=None, height=34, spacing=8)
        id_row.add_widget(Label(text='Key ID:', size_hint_x=None, width=80,
                                halign='right', valign='middle',
                                text_size=(80, 34), font_size='13sp'))
        key_input = TextInput(multiline=False, font_size='13sp')
        id_row.add_widget(key_input)
        content.add_widget(id_row)

        btn_row = BoxLayout(size_hint_y=None, height=40, spacing=10)
        ok_btn = Button(text='OK')
        cancel_btn = Button(text='Cancel')
        btn_row.add_widget(ok_btn)
        btn_row.add_widget(cancel_btn)
        content.add_widget(btn_row)

        popup = Popup(title='Fetch Key from Server', content=content,
                      size_hint=(None, None), size=(450, 220),
                      auto_dismiss=False)

        def on_ok(inst):
            keyserver = ks_spinner.text
            key_id = key_input.text.strip()
            popup.dismiss()
            if key_id:
                self._on_fetch_info(keyserver, key_id)

        def on_cancel(inst):
            popup.dismiss()

        ok_btn.bind(on_release=on_ok)
        cancel_btn.bind(on_release=on_cancel)
        popup.open()

    def _on_fetch_info(self, keyserver, key_id):
        if key_id.startswith('0x'):
            key_id = key_id[2:]

        print(f"Key ID '0x{key_id}' requested")

        if len(key_id) not in [8, 16, 40]:
            self._show_error_message(f"Key ID ({key_id}) is not the correct length!")
            return

        if len(key_id) == 8:
            UiUtils.confirm_dialog(
                None,
                "Careful! Short IDs (8-letter IDs) are easily "
                "duplicated/faked!\n"
                "Are you sure you want to proceed with this "
                "(dangerous) operation?",
                callback=lambda yes: self._do_fetch(keyserver, key_id) if yes else None)
        elif len(key_id) == 16:
            UiUtils.confirm_dialog(
                None,
                "Careful! Long IDs (16-letter IDs) could be "
                "duplicated/faked!\n"
                "Are you sure you want to proceed with this "
                "operation?",
                callback=lambda yes: self._do_fetch(keyserver, key_id) if yes else None)
        else:
            self._do_fetch(keyserver, key_id)

    def _do_fetch(self, keyserver, key_id):
        try:
            fingerprint = GpgUtils.fetch_key(keyserver, key_id)
            if not fingerprint:
                self._show_error_message(
                    f"ERROR! Could not fetch key with ID '0x{key_id}'")
                return
        except Exception as e:
            self._show_error_message(str(e))
            return

        print("Fetched:", fingerprint)
        UiUtils.show_dialog(None,
                            f"Successful import of '0x{key_id}'!\n"
                            f"Fingerprint: {fingerprint}",
                            title="Fetch success",
                            message_type="info")
        self._refresh_key_list()

    def _upload_keys(self, instance):
        print("Upload Keys pressed...")
        UiUtils.show_unimplemented_message_box()

    def _export_keys(self, instance):
        print("Export Keys pressed...")
        UiUtils.show_dialog(None,
                            "This function only exports the public key!",
                            title="Notice")

        key_id = self._selected_keys[0]
        key = GpgUtils.get_key_by_id(key_id)
        key_name = key[2]

        # Turn key name into something FS-friendly
        key_name = key_name.replace('|', '')
        key_name = key_name.replace('<', '(')
        key_name = key_name.replace('>', ')')
        key_name = re.sub(r'[^@a-zA-Z0-9()]+', '_', key_name)
        key_name = re.sub(r'__+', '_', key_name)

        filename, armor = UiUtils.get_save_filename(None, key_name)

        if not filename:
            print("Export cancelled")
            return

        print("Export target:", filename)
        GpgUtils.export_key(key_id, filename, armor)
        print(f"Key exported as {filename}...")

    def _delete_keys(self, instance):
        print("Delete Keys pressed...")
        UiUtils.confirm_dialog(
            None,
            f"Are you sure you want to delete key ids: {self._selected_keys}",
            callback=self._on_delete_confirmed)

    def _on_delete_confirmed(self, confirmed):
        if not confirmed:
            print("Action cancelled!")
            return

        for key in self._selected_keys:
            print("Trying to delete", key[-7:])
            delete_result = GpgUtils.delete_key(key)
            print("Delete key:", delete_result)

        print("Done deleting keys")
        self._refresh_key_list()


class CreateKeyScreen(BaseScreen):
    _window_size = (500, 380)
    _back_target = 'key_management'

    def __init__(self, **kwargs):
        super().__init__(name='create_key', **kwargs)

        layout = BoxLayout(orientation='vertical', padding=15, spacing=8)

        # Form fields
        form = GridLayout(cols=2, spacing=8, size_hint_y=None, height=250,
                          col_default_width=110)

        form.add_widget(Label(text='Name:', halign='right', valign='middle',
                              size_hint_x=None, width=110, text_size=(110, 36),
                              font_size='13sp'))
        self._name_field = TextInput(multiline=False, size_hint_y=None, height=34,
                                     font_size='13sp')
        form.add_widget(self._name_field)

        form.add_widget(Label(text='Email:', halign='right', valign='middle',
                              size_hint_x=None, width=110, text_size=(110, 36),
                              font_size='13sp'))
        self._email_field = TextInput(multiline=False, size_hint_y=None, height=34,
                                      font_size='13sp')
        form.add_widget(self._email_field)

        form.add_widget(Label(text='Key Type:', halign='right', valign='middle',
                              size_hint_x=None, width=110, text_size=(110, 36),
                              font_size='13sp'))
        self._key_type_spinner = KivySpinner(text='RSA', values=['RSA', 'DSA'],
                                             size_hint_y=None, height=34,
                                             font_size='13sp')
        form.add_widget(self._key_type_spinner)

        form.add_widget(Label(text='Key Length:', halign='right', valign='middle',
                              size_hint_x=None, width=110, text_size=(110, 36),
                              font_size='13sp'))
        self._key_length_spinner = KivySpinner(text='4096',
                                               values=['2048', '3072', '4096'],
                                               size_hint_y=None, height=34,
                                               font_size='13sp')
        form.add_widget(self._key_length_spinner)

        form.add_widget(Label(text='Passphrase:', halign='right', valign='middle',
                              size_hint_x=None, width=110, text_size=(110, 36),
                              font_size='13sp'))
        self._passphrase_field = TextInput(password=True, multiline=False,
                                           size_hint_y=None, height=34,
                                           font_size='13sp')
        form.add_widget(self._passphrase_field)

        form.add_widget(Label(text='Confirm:', halign='right', valign='middle',
                              size_hint_x=None, width=110, text_size=(110, 36),
                              font_size='13sp'))
        self._confirm_passphrase_field = TextInput(password=True, multiline=False,
                                                   size_hint_y=None, height=34,
                                                   font_size='13sp')
        form.add_widget(self._confirm_passphrase_field)

        layout.add_widget(form)

        # Spacer
        layout.add_widget(BoxLayout())

        # Status label
        self._status_label = Label(text='', color=(0.6, 0, 0, 1),
                                   size_hint_y=None, height=24, font_size='12sp')
        layout.add_widget(self._status_label)

        # Create button right-aligned
        btn_row = BoxLayout(size_hint_y=None, height=36)
        btn_row.add_widget(BoxLayout())
        self._create_btn = Button(text='Create Key', size_hint_x=None, width=120,
                                  font_size='14sp')
        self._create_btn.bind(on_release=self._do_create)
        btn_row.add_widget(self._create_btn)
        layout.add_widget(btn_row)

        self.add_widget(layout)

    def on_enter(self):
        super().on_enter()
        App.get_running_app().title = 'EZ GPG \u2013 Create Key'

    def on_pre_enter(self):
        self._name_field.text = ''
        self._email_field.text = ''
        self._passphrase_field.text = ''
        self._confirm_passphrase_field.text = ''
        self._status_label.text = ''
        self._create_btn.disabled = False
        self._key_type_spinner.text = 'RSA'
        self._key_length_spinner.text = '4096'

    def _do_create(self, instance):
        print("Clicked Create Key button")

        name = self._name_field.text.strip()
        email = self._email_field.text.strip()
        passphrase = self._passphrase_field.text
        confirmed = self._confirm_passphrase_field.text
        key_type = self._key_type_spinner.text
        key_length = int(self._key_length_spinner.text)

        if not name:
            self._show_error_message("Name is required!")
            return

        if not email:
            self._show_error_message("Email is required!")
            return

        if not passphrase:
            self._show_error_message("Passphrase is required!")
            return

        if passphrase != confirmed:
            self._show_error_message("Passphrases do not match!")
            return

        print(f" - Name: {name}")
        print(f" - Email: {email}")
        print(f" - Key Type: {key_type}")
        print(f" - Key Length: {key_length}")

        self._create_btn.disabled = True
        self._status_label.text = 'Creating key... please wait'

        fingerprint = GpgUtils.create_key(name, email, passphrase, key_type, key_length)

        if fingerprint:
            print(f" - Key created: {fingerprint}")
            UiUtils.show_dialog(None,
                                f"Key created successfully!\n\nFingerprint:\n{fingerprint}",
                                title="Key Created",
                                message_type="info")
            self._go_back()
        else:
            print(" - Key creation failed!")
            self._create_btn.disabled = False
            self._status_label.text = ''
            self._show_error_message("Failed to create key!")


class EzGpg(App):
    title = 'EZ GPG'

    def build(self):
        Window.size = (280, 220)

        sm = ScreenManager(transition=NoTransition())
        sm.add_widget(MainScreen())
        sm.add_widget(EncryptScreen())
        sm.add_widget(DecryptScreen())
        sm.add_widget(SignScreen())
        sm.add_widget(VerifyScreen())
        sm.add_widget(KeyManagementScreen())
        sm.add_widget(CreateKeyScreen())

        # ESC key to go back
        Window.bind(on_keyboard=self._on_keyboard)

        return sm

    def _on_keyboard(self, window, key, *args):
        if key == 27:  # ESC
            sm = self.root
            if sm.current != 'main':
                screen = sm.current_screen
                back = getattr(screen, '_back_target', 'main')
                sm.transition = NoTransition()
                sm.current = back
                return True
        return False

    @staticmethod
    def launch():
        print("Launching app")
        EzGpg().run()
