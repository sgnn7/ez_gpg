# vim:ff=unix ts=4 sw=4 expandtab

import gi
import os

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')

from gi.repository import Gdk, Gio, GLib, Gtk

from .utils import EzGpgUtils

class GenericWindow(Gtk.Window):
    def __init__(self, app, window_name, title, ):
        window_title = "EZ GPG - %s" % title

        self._app = app

        Gtk.Window.__init__(self, title = window_title, application = app)

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
            simple_action = Gio.SimpleAction.new(action, None)
            simple_action.connect('activate', callback)
            app.add_action(simple_action)

            self._mapped_actions[action] = simple_action

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
        EzGpgUtils.show_dialog(self,
                               message)

class MainWindow(GenericWindow):
    def __init__(self, app):
        super().__init__(app, 'main_window', "Home")

        builder = Gtk.Builder()
        builder.add_from_file('data/main_window.ui')

        self.add(builder.get_object('main_window_vbox'))

        self._shown_window = None

    def _get_actions(self):
        return [ ('show_encrypt_ui', self.show_encrypt_ui),
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

    def show_encrypt_ui(self, action = None, param = None):
        print("Clicked Encrypt button")
        self._show_window(EncryptWindow)

    def show_decrypt_ui(self, action = None, param = None):
        print("Clicked Decrypt button")
        EzGpgUtils.show_unimplemented_message_box(self)

    def show_sign_ui(self, action = None, param = None):
        print("Clicked Sign button")
        self._show_window(SignWindow)

    def show_verify_ui(self, action = None, param = None):
        print("Clicked Verify button")
        self._show_window(VerifyWindow)

    def show_key_management_ui(self, action = None, param = None):
        print("Clicked Key Management button")
        EzGpgUtils.show_unimplemented_message_box(self)

class EncryptWindow(GenericWindow):
    def __init__(self, app):
        super().__init__(app, 'encrypt_window', "Encrypt")

        builder = Gtk.Builder()
        builder.add_from_file('data/encrypt_window.ui')

        self._key_list_box = builder.get_object('lst_key_selection')
        self._file_chooser = builder.get_object('fc_main')
        self._armor_output_check_box = builder.get_object('chk_armor')
        self._encrypt_spinner = builder.get_object('spn_encrypt')
        self._encrypt_button = builder.get_object('btn_do_encrypt')

        # XXX: Armor param doesn't seem to produce armored output so we
        #      disable this for now
        self._armor_output_check_box.set_visible(False)

        for key_id, key_name, key_friendly_name in EzGpgUtils.get_gpg_keys():
            key_row = Gtk.CheckButton(key_friendly_name)
            key_row.set_name(key_id)

            self._key_list_box.add(key_row)

        self._key_list_box.show_all()

        self.add(builder.get_object('encrypt_window_vbox'))

    def _get_actions(self):
        return [ ('encrypt_window.do_encrypt', self.do_encrypt),
               ]

    def do_encrypt(self, action = None, param = None):
        print("Clicked Encrypt Content button")

        # TODO: Make this event driven vs post verification
        print(" - Checking source file(s)")

        filenames = self._file_chooser.get_filenames()
        print("   - Filenames:", filenames)

        if len(filenames) < 1:
            self._show_error_message("File not selected!")
            return

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

        use_armor = self._armor_output_check_box.get_active()
        print("Armor output: %s" % use_armor)

        # Disable encrypt button if we're in the middle of encryption
        print(" - Locking UI and showing spinner.")
        self._encrypt_button.set_sensitive(False)
        self._encrypt_spinner.start()

        # XXX / TODO: We're having our main thread blocked by gnupg work
        #             so we need to add threading at some point.
        def finished_encryption_cb(self):
            print(" - Finished. Stopping spinner.")
            self._encrypt_spinner.stop()

        EzGpgUtils.encrypt_files(self, filenames, selected_keys, use_armor,
                                 callback = finished_encryption_cb)

        self.destroy()

class SignWindow(GenericWindow):
    def __init__(self, app):
        super().__init__(app, 'sign_window', "Sign file")

        builder = Gtk.Builder()
        builder.add_from_file('data/sign_window.ui')

        self._source_file = builder.get_object('fc_source_file')

        self._key_list = builder.get_object('cmb_key_list')
        EzGpgUtils.add_gpg_keys_to_combo_box(self._key_list)

        self._password_field = builder.get_object('ent_password')

        self._armor_output_check_box = builder.get_object('chk_armor')
        self._sign_spinner = builder.get_object('spn_sign')
        self._sign_button = builder.get_object('btn_do_sign')

        # XXX: Armor param doesn't seem to produce armored output so we
        #      disable this for now
        self._armor_output_check_box.set_visible(False)


        self.add(builder.get_object('sign_window_vbox'))

    def _get_actions(self):
        return [ ('sign_window.do_sign', self.do_sign),
               ]

    def do_sign(self, action = None, param = None):
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

        EzGpgUtils.sign_file(self, source_file, selected_key,
                             callback = finished_encryption_cb)

        self.destroy()

class VerifyWindow(GenericWindow):
    def __init__(self, app):
        super().__init__(app, 'verify_window', "Verify Signature")

        builder = Gtk.Builder()
        builder.add_from_file('data/verify_window.ui')

        self._source_file = builder.get_object('fc_source_file')
        self._signature_file = builder.get_object('fc_signature_file')
        self._verify_button = builder.get_object('btn_do_verify')

        self.add(builder.get_object('verify_window_vbox'))

    def _get_actions(self):
        return [ ('verify_window.do_verify', self.do_verify),
               ]

    def do_verify(self, action = None, param = None):
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

        EzGpgUtils.verify_file(self, source_file, signature_file)

        self.destroy()

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
            css_file = Gio.File.new_for_uri('file:///%s/application.css' % current_dir)
            css_provider = Gtk.CssProvider()
            css_provider.load_from_file(css_file)

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

    def on_about(self, action = None, param = None):
        print("About button pressed")
        about_dialog = Gtk.AboutDialog(transient_for=self._window, modal=True)
        about_dialog.present()

    def on_quit(self, action = None, param = None):
        print("Quitting...")
        self._window.destroy()

        self.quit()
