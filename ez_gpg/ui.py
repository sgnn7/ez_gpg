# vim:ff=unix ts=4 sw=4 expandtab

import gi
import os

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')

from gi.repository import Gdk, Gio, GLib, Gtk

from .utils import EzGpgUtils

class GpgKeyList(Gtk.ComboBox):
    def __init__(self):
        Gtk.ComboBox.__init__(self)

        self.set_name('gpg_key_list')

        gpg_keys_list = Gtk.ListStore(str, str)
        for key_id, key_name, key_friendly_name in EzGpgUtils.get_gpg_keys():
            gpg_keys_list.append([key_id, key_friendly_name])

        cell = Gtk.CellRendererText()
        self.pack_start(cell, True)
        self.add_attribute(cell, 'text', 1)

        self.set_model(gpg_keys_list)
        self.set_entry_text_column(1)

class GenericWindow(Gtk.Window):
    def __init__(self, app, window_name, title):
        window_title = "EZ GPG - %s" % title

        self._app = app

        Gtk.Window.__init__(self, title = window_title, application = app)

        self.set_border_width(20)
        self.set_name(window_name)
        self.set_position(Gtk.WindowPosition.CENTER)

        self.connect("delete-event", self._close_window)

        self._mapped_actions = {}
        for action, callback in self._get_actions():
            simple_action = Gio.SimpleAction.new(action, None)
            simple_action.connect('activate', callback)
            app.add_action(simple_action)

            self._mapped_actions[action] = simple_action

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

    def show_encrypt_ui(self, action = None, param = None):
        print("Clicked Encrypt button")
        child_window = EncryptWindow(self._app)
        child_window.set_modal(True)
        child_window.set_transient_for(self)

        child_window.show_all()

        self._app.add_window(child_window)

    def show_decrypt_ui(self, action = None, param = None):
        print("Clicked Decrypt button")
        EzGpgUtils.show_unimplemented_message_box(self)

    def show_sign_ui(self, action = None, param = None):
        print("Clicked Sign button")
        EzGpgUtils.show_unimplemented_message_box(self)

    def show_verify_ui(self, action = None, param = None):
        print("Clicked Verify button")
        EzGpgUtils.show_unimplemented_message_box(self)

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

        for key_id, key_name, key_friendly_name in EzGpgUtils.get_gpg_keys():
            key_row = Gtk.CheckButton(key_friendly_name)
            key_row.set_name(key_id)

            self._key_list_box.add(key_row)

        self.add(builder.get_object('encrypt_window_vbox'))

    def _get_actions(self):
        return [ ('encrypt_window.do_encrypt', self.do_encrypt),
               ]

    def do_encrypt(self, action = None, param = None):
        print("Clicked Encrypt Content button")

        # TODO: Make this event driven vs post verification
        print(" - Checking source file(s)")
        filename = self._file_chooser.get_filename()
        if not filename:
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

        EzGpgUtils.encrypt_file(self, filename, selected_keys)

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
