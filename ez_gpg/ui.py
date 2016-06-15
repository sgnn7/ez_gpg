import gi
import gnupg  # Requires python3-gnupg
import os

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')

from gi.repository import Gdk, Gio, GLib, Gtk

class GpgKeyList(Gtk.ComboBox):
    def __init__(self):
        Gtk.ComboBox.__init__(self)

        self.set_name('gpg_key_list')

        gpg_keys_list = Gtk.ListStore(str, str)
        for key_id, key_name, key_friendly_name in self._get_gpg_keys():
            gpg_keys_list.append([key_id, key_friendly_name])

        cell = Gtk.CellRendererText()
        self.pack_start(cell, True)
        self.add_attribute(cell, 'text', 1)

        self.set_model(gpg_keys_list)
        self.set_entry_text_column(1)

    def _get_gpg_keys(self):
        gpg = gnupg.GPG()

        keys = []

        for key in gpg.list_keys():
            key_id = key['keyid']
            key_friendly_name = key['uids'][0]

            key_name = "%s %s" % (key_id, key_friendly_name)

            keys.append((key_id, key_name, key_friendly_name))

        keys.sort(key=lambda key_tuple: key_tuple[2])

        return keys

class GenericWindow(Gtk.Window):
    def __init__(self, app, window_name, title):
        window_title = "EZ GPG - %s" % title

        Gtk.Window.__init__(self, title = window_title, application = app)

        self.set_border_width(20)
        self.set_name(window_name)
        self.set_position(Gtk.WindowPosition.CENTER)

class MainWindow(GenericWindow):
    def __init__(self, app):
        super().__init__(app, 'main_window', "Home")

        builder = Gtk.Builder()
        builder.add_from_file('data/main_window.ui')

        self.add(builder.get_object('main_window_vbox'))

class EncryptWindow(GenericWindow):
    def __init__(self, app):
        super().__init__(app, 'encrypt_window', "Encrypt")

        builder = Gtk.Builder()
        builder.add_from_file('data/encrypt_window.ui')

        self.add(builder.get_object('encrypt_window_vbox'))


class EzGpg(Gtk.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id="org.sgnn7.ezgpg",
                         flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
                         **kwargs)

        GLib.set_application_name("Ez Gpg")
        GLib.set_prgname('EZ GPG')

        self._window = None

        self._actions = [
            ('about', True, self.on_about),
            ('quit',  True, self.on_quit),

            ('encrypt_content', False, self.show_encrypt_ui),
            ('decrypt_content', False, self.show_decrypt_ui),
            ('sign_content',    False, self.show_sign_ui),
            ('verify_content',  False, self.show_verify_ui),
            ('key_management',  False, self.show_key_management_ui),
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

    def show_encrypt_ui(self, action = None, param = None):
        print("Clicked Encrypt button")
        self._show_unimplemented_message_box()

    def show_decrypt_ui(self, action = None, param = None):
        print("Clicked Decrypt button")
        self._show_unimplemented_message_box()

    def show_sign_ui(self, action = None, param = None):
        print("Clicked Sign button")
        self._show_unimplemented_message_box()

    def show_verify_ui(self, action = None, param = None):
        print("Clicked Verify button")
        self._show_unimplemented_message_box()

    def show_key_management_ui(self, action = None, param = None):
        print("Clicked Key Management button")
        self._show_unimplemented_message_box()

    def _show_unimplemented_message_box(self):
        dialog = Gtk.MessageDialog(self._window, 0,
                                   Gtk.MessageType.WARNING,
                                   Gtk.ButtonsType.OK,
                                   "Not Implemented")
        dialog.format_secondary_text("This functionality is not yet implemented!")

        response = dialog.run()

        dialog.destroy()

    def do_command_line(self, command_line):
        # options = command_line.get_options_dict()

        # if options.contains("test"):
        #     pass
        # self.activate()
        # return 0

        self.activate()

        return 0

    def on_about(self, action = None, param = None):
        about_dialog = Gtk.AboutDialog(transient_for=self._window, modal=True)
        about_dialog.present()

    def on_quit(self, action = None, param = None):
        print("Quitting...")
        self._window.destroy()

        self.quit()
