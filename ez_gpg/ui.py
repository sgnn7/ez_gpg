# vim:ff=unix ts=4 sw=4 expandtab

import gi
import os
import pkg_resources
import re

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')

from gi.repository import Gdk, Gio, GLib, GObject, Gtk

from .config import Config
from .gpg_utils import GpgUtils
from .ui_utils import error_wrapper, UiUtils

class GenericWindow(Gtk.Window):
    def __init__(self, app, window_name, title,
                 glade_file=None):
        window_title = "EZ GPG - %s" % title

        self._app = app

        Gtk.Window.__init__(self, title=window_title, application=app)

        self.set_border_width(20)
        self.set_name(window_name)
        self.set_position(Gtk.WindowPosition.CENTER)

        # TODO: We need our own icon
        try:
            self.set_icon_name("seahorse")
        except:
            pass

        self.connect("delete-event", self._close_window)
        self.connect("key-press-event", self._on_key_pressed)

        self._mapped_actions = {}
        for action, callback in self._get_actions():
            # print("Mapping %s to %s" % (action, callback))
            simple_action = Gio.SimpleAction.new(action, None)
            simple_action.connect('activate', error_wrapper(callback))
            app.add_action(simple_action)

            self._mapped_actions[action] = simple_action

        if not glade_file:
            glade_file = window_name

        self._build_ui(glade_file)

    def _on_key_pressed(self, widget, event):
        # TODO: Maybe use accelerators?
        if event.keyval == Gdk.KEY_Escape:
            self._close_window()

        return False

    def _close_window(self, *args, **kwargs):
        self.destroy()

    def _get_actions(self):
        return []

    def _show_error_message(self, message):
        print("ERROR! %s" % message)
        UiUtils.show_dialog(self,
                            message)

    def confirm_action(self, message):
        return UiUtils.confirm_dialog(self, message)

    def get_builder(self):
        return self._builder

    def _build_ui(self, glade_file):
        self._builder = Gtk.Builder()

        ui_filename = pkg_resources.resource_filename('ez_gpg',
                                                      'data/%s.ui' % glade_file)
        self._builder.add_from_file(ui_filename)


class MainWindow(GenericWindow):
    def __init__(self, app):
        super().__init__(app, 'main_window', "Home")

        self.add(self.get_builder().get_object('main_window_vbox'))

    def _get_actions(self):
        return [('show_encrypt_ui', self.show_encrypt_ui),
                ('show_decrypt_ui', self.show_decrypt_ui),
                ('show_sign_ui',    self.show_sign_ui),
                ('show_verify_ui',  self.show_verify_ui),
                ('key_management',  self.show_key_management_ui),
                ]

    def _show_window(self, clazz):
        child_window = clazz(self._app)
        child_window.set_modal(True)
        child_window.set_transient_for(self)

        child_window.present()

        self._app.add_window(child_window)

    def show_encrypt_ui(self, action=None, param=None):
        print("Clicked Encrypt button")
        self._show_window(EncryptWindow)

    def show_decrypt_ui(self, action=None, param=None):
        print("Clicked Decrypt button")
        self._show_window(DecryptWindow)

    def show_sign_ui(self, action=None, param=None):
        print("Clicked Sign button")
        self._show_window(SignWindow)

    def show_verify_ui(self, action=None, param=None):
        print("Clicked Verify button")
        self._show_window(VerifyWindow)

    def show_key_management_ui(self, action=None, param=None):
        print("Clicked Key Management button")
        self._show_window(KeyManagementWindow)


class KeyManagementWindow(GenericWindow):
    def __init__(self, app):
        super().__init__(app, 'key_management', "Key Management")

        builder = self.get_builder()

        # XXX: Keeping state is bad but we can fix this later
        self._selected_keys = []

        self._key_list_box = builder.get_object('lst_keys')
        self._refresh_key_list()

        self._keyserver_combo = builder.get_object('cmb_keyserver')

        # Populate keyserver list
        keyserver_list = Gtk.ListStore(str, str)
        for keyserver in Config.get_keyservers():
            keyserver_list.append([keyserver, keyserver])

        cell = Gtk.CellRendererText()
        self._keyserver_combo.pack_start(cell, True)
        self._keyserver_combo.add_attribute(cell, 'text', 1)

        self._keyserver_combo.set_model(keyserver_list)
        self._keyserver_combo.set_id_column(0)
        self._keyserver_combo.set_entry_text_column(1)

        # Set default keyserver
        self._keyserver_combo.set_active(0)

        self._edit_key_button = builder.get_object('btn_edit')
        self._upload_key_button = builder.get_object('btn_upload')
        self._export_key_button = builder.get_object('btn_export')
        self._delete_key_button = builder.get_object('btn_delete')

        self.add(builder.get_object('main_vbox'))

        self._update_button_state()

    def _refresh_key_list(self):
        for child in self._key_list_box.get_children():
            self._key_list_box.remove(child)
            # child.destroy()
            # TODO: Disconnect notify::active signal

        for key in GpgUtils.get_gpg_keys():
            key_id = key[0]
            key_friendly_name = key[2]

            key_row = Gtk.CheckButton(GObject.markup_escape_text(key_friendly_name))
            key_row.get_children()[0].set_use_markup(True)
            key_row.set_name(key_id)

            key_row.connect('notify::active', self._key_changed_active_state)

            self._key_list_box.add(key_row)

        self._key_list_box.show_all()

    def _get_actions(self):
        return [('key_management_window.do_create_key',  self.create_keys),
                ('key_management_window.do_import_keys', self.import_keys),
                ('key_management_window.do_edit_keys',   self.edit_keys),
                ('key_management_window.do_fetch_keys',  self.fetch_keys),
                ('key_management_window.do_upload_keys', self.upload_keys),
                ('key_management_window.do_export_keys', self.export_keys),
                ('key_management_window.do_delete_keys', self.delete_keys),
                ]

    def _key_changed_active_state(self, widget, params):
        key_id = widget.get_name()
        self._selected_keys = [key for key in self._selected_keys if key != key_id]
        if widget.get_active():
            self._selected_keys.append(key_id)

        print("New selection list:")
        for key in self._selected_keys:
            print("Key:", key[-Config.KEY_ID_SIZE:])

        self._update_button_state()

    def _update_button_state(self):
        self._edit_key_button.set_sensitive(len(self._selected_keys) == 1)
        self._export_key_button.set_sensitive(len(self._selected_keys) == 1)
        self._upload_key_button.set_sensitive(len(self._selected_keys) > 0)
        self._delete_key_button.set_sensitive(len(self._selected_keys) > 0)

    def create_keys(self, action=None, param=None):
        print("Create Keys pressed...")
        UiUtils.show_unimplemented_message_box(self)

    def edit_keys(self, action=None, param=None):
        print("Edit Keys pressed...")
        UiUtils.show_unimplemented_message_box(self)

    def import_keys(self, action=None, param=None):
        print("Import Keys pressed...")
        filename = UiUtils.get_filename(self)
        if filename:
            print("Chosen file to import:", filename)
            if GpgUtils.import_key(filename):
                # TODO: Make the new key bold
                self._refresh_key_list()
            else:
                UiUtils.show_dialog(self,
                                    "ERROR! Keyfile could not be imported",
                                    title="Keyfile error")

    def export_keys(self, action=None, param=None):
        print("Export Keys pressed...")
        UiUtils.show_dialog(self,
                            "This function only exports the public key!",
                            title="Notice")

        key_id = self._selected_keys[0]
        key = GpgUtils.get_key_by_id(key_id)
        key_name = key[2]

        # Turn key name into something FS-friendly
        # XXX: There's probably a better way to do this
        key_name = key_name.replace('|','')
        key_name = key_name.replace('<','(')
        key_name = key_name.replace('>',')')
        key_name = re.sub(r'[^@a-zA-Z0-9()]+','_', key_name)
        key_name = re.sub(r'__+','_', key_name)

        filename, armor = UiUtils.get_save_filename(self, key_name)

        if not filename:
            print("Export cancelled")
            return

        print("Export target:", filename)

        GpgUtils.export_key(key_id, filename, armor)

        print("Key exported as %s..." % filename)

    def upload_keys(self, action=None, param=None):
        print("Upload Keys pressed...")
        UiUtils.show_unimplemented_message_box(self)

    def fetch_keys(self, action=None, param=None):
        print("Fetch Keys pressed...")
        key_id = UiUtils.get_string_from_user(self, "Enter key ID to fetch from server:",
                                              max_length=42)

        if not key_id:
            print("Fetch cancelled")
            return

        if key_id.startswith('0x'):
            key_id = key_id[2:]

        # TODO: Check that the string is hex

        print("Key ID '0x%s' requested" % key_id)

        if len(key_id) not in [ 8, 16, 40 ]:
            self._show_error_message("Key ID (%s) is not the correct length!" % key_id)
            return

        if len(key_id) == 8:
            do_it = UiUtils.confirm_dialog(self,
                                           "Careful! Short IDs (8-letter IDs) are easily " +
                                           "duplicated/faked!\n" +
                                           "Are you sure you want to proceed with this " +
                                           "(dangerous) operation?")
            if not do_it:
                return

        if len(key_id) == 16:
            do_it = UiUtils.confirm_dialog(self,
                                           "Careful! Long IDs (16-letter IDs) could be " +
                                           "duplicated/faked!\n" +
                                           "Are you sure you want to proceed with this "
                                           "operation?")
            if not do_it:
                return

        keyserver = self._keyserver_combo.get_active_id()
        try:
            fingerprint = GpgUtils.fetch_key(keyserver, key_id)
            if not fingerprint:
                self._show_error_message("ERROR! Could not fetch key with ID '0x%s'" % key_id)
                return
        except Exception as e:
            self._show_error_message(str(e))
            return

        print("Fetched:", fingerprint)
        UiUtils.show_dialog(self,
                            "Successful import of '0x%s':!\n" % key_id +
                            "Fingerprint: " + fingerprint,
                            title="Fetch success",
                            message_type=Gtk.MessageType.INFO)

    def delete_keys(self, action=None, param=None):
        print("Delete Keys pressed...")
        if not self.confirm_action("Are you sure you want to delete key ids: %s" % self._selected_keys):
            print("Action cancelled!")
            return

        # TODO: Show which keys we're deleting
        for key in self._selected_keys:
            print("Trying to delete", key[-7:])
            delete_result = GpgUtils.delete_key(key)
            print("Delete key:", delete_result)

            if delete_result:
                self._refresh_key_list()

        print("Done deleting keys")

class EncryptWindow(GenericWindow):
    def __init__(self, app):
        super().__init__(app, 'encrypt_window', "Encrypt")

        builder = self.get_builder()

        self._key_list_box = builder.get_object('lst_key_selection')
        self._file_chooser = builder.get_object('fc_main')
        self._armor_output_check_box = builder.get_object('chk_armor')
        self._encrypt_spinner = builder.get_object('spn_encrypt')
        self._encrypt_button = builder.get_object('btn_do_encrypt')

        self._encryption_type = builder.get_object('ntb_encryption_type')
        self._password_field = builder.get_object('ent_password')
        self._confirm_password_field = builder.get_object('ent_confirm_password')

        # XXX: Armor param doesn't seem to produce armored output so we
        #      disable this for now
        self._armor_output_check_box.set_visible(False)

        for key in GpgUtils.get_gpg_keys():
            key_id = key[0]
            key_friendly_name = key[2]

            key_row = Gtk.CheckButton(key_friendly_name)
            key_row.set_name(key_id)

            self._key_list_box.add(key_row)

        self._key_list_box.show_all()

        builder.connect_signals({'password_changed': self._check_password_matching})

        self.add(builder.get_object('encrypt_window_vbox'))

    def _get_actions(self):
        return [('encrypt_window.do_encrypt', self.do_encrypt),
                ]

    def _check_password_matching(self, widget):
        window = widget.get_toplevel()
        password_field = window._password_field
        confirm_password_field = window._confirm_password_field

        password = password_field.get_text()
        confirmed_password = confirm_password_field.get_text()

        if password == None or confirmed_password == None:
            confirm_password_field.set_icon_from_stock(1, None)
        else:
            if password == confirmed_password:
                confirm_password_field.set_icon_from_stock(1, None)
            else:
                confirm_password_field.set_icon_from_stock(1, Gtk.STOCK_DIALOG_ERROR)
                confirm_password_field.set_icon_tooltip_text(1, "Passwords do not match!")

    def do_encrypt(self, action=None, param=None):
        print("Clicked Encrypt Content button")

        # TODO: Make this event driven vs post verification
        print(" - Checking source file(s)")

        filenames = self._file_chooser.get_filenames()
        print("   - Filenames:", filenames)

        if len(filenames) < 1:
            self._show_error_message("File not selected!")
            return

        use_armor = self._armor_output_check_box.get_active()
        print("Armor output: %s" % use_armor)

        is_pki_encryption = self._encryption_type.get_current_page() == 0
        print(" Using PKI:", is_pki_encryption)

        if is_pki_encryption:
            self._encrypt_pki(filenames, use_armor)
        else:
            self._encrypt_symetric(filenames, use_armor)


    def _encrypt_symetric(self, filenames, use_armor):
        password_field = self._password_field
        confirm_password_field = self._confirm_password_field

        password = password_field.get_text()
        confirmed_password = confirm_password_field.get_text()

        if password == None or confirmed_password == None:
            self._show_error_message("No password set!")
            return
        elif password != confirmed_password:
            self._show_error_message("Passwords do not match!")
            return

        print(" - Locking UI and showing spinner.")
        self._encrypt_button.set_sensitive(False)
        self._encrypt_spinner.start()

        # XXX / TODO: We're having our main thread blocked by gnupg work
        #             so we need to add threading at some point.
        def finished_encryption_cb(self):
            print(" - Finished. Stopping spinner.")
            self._encrypt_spinner.stop()

        GpgUtils.encrypt_files_symetric(self, filenames, password,
                                        use_armor, callback=finished_encryption_cb)

        self.destroy()



    def _encrypt_pki(self, filenames, use_armor):
        print(" - Checking GPG key selection")
        selected_keys = []
        for list_box_row in self._key_list_box.get_children():
            key_item = list_box_row.get_children()[0]
            if key_item.get_active():
                key_id = key_item.get_name()

                print("   - Selected: %s" % key_id)
                selected_keys.append(key_id)

        # TODO: Make this event driven vs post verification
        if len(selected_keys) == 0:
            self._show_error_message("No key selected!")
            return

        # Disable encrypt button if we're in the middle of encryption
        print(" - Locking UI and showing spinner.")
        self._encrypt_button.set_sensitive(False)
        self._encrypt_spinner.start()

        # XXX / TODO: We're having our main thread blocked by gnupg work
        #             so we need to add threading at some point.
        def finished_encryption_cb(self):
            print(" - Finished. Stopping spinner.")
            self._encrypt_spinner.stop()

        GpgUtils.encrypt_files_pki(self, filenames, selected_keys,
                                   use_armor, callback=finished_encryption_cb)

        self.destroy()

class SignWindow(GenericWindow):
    def __init__(self, app):
        super().__init__(app, 'sign_window', "Sign file")

        builder = self.get_builder()

        self._source_file = builder.get_object('fc_source_file')

        self._key_list = builder.get_object('cmb_key_list')
        GpgUtils.add_gpg_keys_to_combo_box(self._key_list, True)

        self._password_field = builder.get_object('ent_password')

        self._armor_output_check_box = builder.get_object('chk_armor')
        self._sign_spinner = builder.get_object('spn_sign')
        self._sign_button = builder.get_object('btn_do_sign')

        # XXX: Armor param doesn't seem to produce armored output so we
        #      disable this for now
        self._armor_output_check_box.set_visible(False)

        builder.connect_signals({'password_changed': self._check_key_password,
                                 'key_changed': self._check_key_password})

        self.add(builder.get_object('sign_window_vbox'))

    def _get_actions(self):
        return [('sign_window.do_sign', self.do_sign),
                ]

    def _check_key_password(self, widget):
        window = widget.get_toplevel()
        password_field = window._password_field
        selected_key = self._key_list.get_active_id()
        if selected_key:
            if GpgUtils.check_key_password(selected_key, password_field.get_text()):
                password_field.set_icon_from_stock(1, None)
            else:
                password_field.set_icon_from_stock(1, Gtk.STOCK_DIALOG_ERROR)
                password_field.set_icon_tooltip_text(1, "Invalid password for the selected key!")

    def do_sign(self, action=None, param=None):
        print("Clicked Sign button")

        # TODO: Make this event driven vs post verification
        print(" - Checking source file(s)")
        source_file = self._source_file.get_filename()
        if not source_file:
            self._show_error_message("File not selected!")
            return

        print(" - Checking GPG key selection")
        selected_key = self._key_list.get_active_id()
        # TODO: Make this event driven vs post verification
        if not selected_key:
            self._show_error_message("No key selected!")
            return

        print(" - Key Id:", selected_key)

        use_armor = self._armor_output_check_box.get_active()
        print(" - Armor output: %s" % use_armor)

        # Disable encrypt button if we're in the middle of encryption
        print(" - Locking UI and showing spinner.")
        self._sign_button.set_sensitive(False)
        self._sign_spinner.start()

        # XXX / TODO: We're having our main thread blocked by gnupg work
        #             so we need to add threading at some point.
        def finished_encryption_cb(self):
            print(" - Finished. Stopping spinner.")
            self._sign_spinner.stop()
            self._sign_button.set_sensitive(True)

        success = GpgUtils.sign_file(self, source_file, selected_key,
                                       self._password_field.get_text(),
                                       callback=finished_encryption_cb)

        if success:
            self.destroy()
        else:
            finished_encryption_cb(self)


class DecryptWindow(GenericWindow):
    def __init__(self, app):
        super().__init__(app, 'decrypt_window', "Decrypt file")

        builder = self.get_builder()

        self._source_file = builder.get_object('fc_source_file')

        self._key_list = builder.get_object('cmb_key_list')
        GpgUtils.add_gpg_keys_to_combo_box(self._key_list, True)

        # TODO: Use a real ID
        self._key_list.get_model().append(['symetric',
                                           'Symetric encryption (password only)'])

        # Prefetch the list
        self._gpg_keys = GpgUtils.get_gpg_keys(True)

        # Install a filter
        self._key_filter = self._key_list.get_model().filter_new()
        self._key_filter.set_visible_func(self._filter_key_ids)
        self._key_list.set_model(self._key_filter)

        self._password_field = builder.get_object('ent_password')

        self._armor_output_check_box = builder.get_object('chk_armor')
        self._decrypt_spinner = builder.get_object('spn_decrypt')
        self._decrypt_button = builder.get_object('btn_do_decrypt')

        builder.connect_signals({'password_changed': self._check_key_password,
                                 'key_changed': self._check_key_password,
                                 'file_chosen': self._update_key_list})

        self.add(builder.get_object('decrypt_window_vbox'))

    def _get_actions(self):
        return [('decrypt_window.do_decrypt', self.do_decrypt),
                ]

    # XXX: Nasty but no easy way to compare subkeys for all items with
    #      inconsistent lengths between two arrays
    def _filter_key_ids(self, model, iter, data):
        if not self._source_file.get_filename():
            return False

        info = self._encrypted_file_info

        if info.is_symetric:
            return model[iter][0] == 'symetric'

        matching_keys = list(filter(lambda x: x[0] == model[iter][0], self._gpg_keys))
        if len(matching_keys) == 0:
            return False

        key_id, key_name, key_friendly_name, subkeys, _ = matching_keys[0]
        for subkey in subkeys:
            # print("Comparing %s in %s" % (subkey, info.key_ids))
            for encryption_key in info.key_ids:
                if subkey.endswith(encryption_key):
                    print("Found! Matching key:", key_id, key_name)
                    info.matching_key = key_id
                    return True

        return False

    def _update_key_list(self, widget):
        print("File changed - checking for key_ids...")
        self._encrypted_file_info = GpgUtils.get_encryped_file_info(self,
                                                                      widget.get_filename())

        info = self._encrypted_file_info
        if not info:
            return

        if info.is_symetric:
            print("Symetric encryption")
            self._key_filter.refilter()
            self._key_list.set_active_id('symetric')
        else:
            print("Keys: ", info.key_ids)
            self._key_filter.refilter()

            if info.matching_key:
                self._key_list.set_active_id(info.matching_key)
            else:
                UiUtils.show_dialog(self,
                                    "ERROR! You do not have a key that decrypt this file!",
                                    title="Missing decryption key")

        self._check_key_password(widget)

    def _check_key_password(self, widget):
        window = widget.get_toplevel()
        password_field = window._password_field
        selected_key = self._key_list.get_active_id()

        if not selected_key or \
           selected_key == 'symetric':
            password_field.set_icon_from_stock(1, None)
        else:
            if GpgUtils.check_key_password(selected_key, password_field.get_text()):
                password_field.set_icon_from_stock(1, None)
            else:
                password_field.set_icon_from_stock(1, Gtk.STOCK_DIALOG_ERROR)
                password_field.set_icon_tooltip_text(1, "Invalid password for the selected key!")

    def do_decrypt(self, action=None, param=None):
        print("Clicked Decrypt button")

        # TODO: Make this event driven vs post verification
        print(" - Checking source file(s)")
        source_file = self._source_file.get_filename()
        if not source_file:
            self._show_error_message("File not selected!")
            return

        selected_key = self._key_list.get_active_id()
        print(" - Key Id:", selected_key)

        # Disable encrypt button if we're in the middle of encryption
        print(" - Locking UI and showing spinner.")
        self._decrypt_button.set_sensitive(False)
        self._decrypt_spinner.start()

        # XXX / TODO: We're having our main thread blocked by gnupg work
        #             so we need to add threading at some point.
        def finished_decryption_cb(self):
            print(" - Finished. Stopping spinner.")
            self._decrypt_spinner.stop()
            self._decrypt_button.set_sensitive(True)

        success = GpgUtils.decrypt_file(self, source_file,
                                          self._password_field.get_text(),
                                          callback=finished_decryption_cb)

        if success:
            self.destroy()
        else:
            finished_decryption_cb(self)


class VerifyWindow(GenericWindow):
    def __init__(self, app):
        super().__init__(app, 'verify_window', "Verify Signature")

        builder = self.get_builder()

        self._source_file = builder.get_object('fc_source_file')
        self._signature_file = builder.get_object('fc_signature_file')
        self._verify_button = builder.get_object('btn_do_verify')

        self.add(builder.get_object('verify_window_vbox'))

    def _get_actions(self):
        return [('verify_window.do_verify', self.do_verify),
                ]

    def do_verify(self, action=None, param=None):
        print("Clicked Verify Signature button")

        # TODO: Make this event driven vs post verification
        print(" - Checking source file(s)")
        source_file = self._source_file.get_filename()
        if not source_file:
            self._show_error_message("File not selected!")
            return

        signature_file = self._signature_file.get_filename()
        print(" - Using signature file:", signature_file)

        # Disable verify button if we're in the middle of verification
        self._verify_button.set_sensitive(False)

        if GpgUtils.verify_file(self, source_file, signature_file):
            self.destroy()
        else:
            self._verify_button.set_sensitive(True)


class EzGpg(Gtk.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id="org.sgnn7.ezgpg",
                         flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
                         **kwargs)

        GLib.set_application_name("Ez Gpg")
        GLib.set_prgname('EZ GPG')

        self._window = None
        self._encrypt_window = None

        self._actions = [
            ('about', True, self.on_about),
            ('quit',  True, self.on_quit),
        ]

    def do_startup(self):
        print("Starting up...")
        Gtk.Application.do_startup(self)

        menu = Gio.Menu()

        for action, is_menu_item, callback in self._actions:
            if is_menu_item:
                menu.append(action.capitalize(), "app.%s" % action)

            simple_action = Gio.SimpleAction.new(action, None)
            simple_action.connect('activate', callback)
            self.add_action(simple_action)

        self.set_app_menu(menu)

    def do_activate(self):
        print("Activating...")
        if not self._window:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            css_provider = Gtk.CssProvider()
            css_provider.load_from_path(pkg_resources.resource_filename('ez_gpg',
                                                                        'data/application.css'))

            screen = Gdk.Screen.get_default()
            style_context = Gtk.StyleContext()
            style_context.add_provider_for_screen(screen,
                                                  css_provider,
                                                  Gtk.STYLE_PROVIDER_PRIORITY_USER)

            self._window = MainWindow(self)
            self._window.show_all()

        self.add_window(self._window)

        self._window.present()

    def do_command_line(self, command_line):
        # options = command_line.get_options_dict()

        # if options.contains("test"):
        #     pass
        # self.activate()
        # return 0

        self.activate()

        return 0

    def on_about(self, action=None, param=None):
        print("About button pressed")
        about_dialog = Gtk.AboutDialog(transient_for=self._window, modal=True)
        about_dialog.present()

    def on_quit(self, action=None, param=None):
        print("Quitting...")
        self._window.destroy()

        self.quit()

    @staticmethod
    def launch():
        print("Launching app")
        EzGpg().run()
