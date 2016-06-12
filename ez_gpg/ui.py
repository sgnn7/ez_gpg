import gi
import gnupg  # Requires python3-gnupg

gi.require_version('Gtk', '3.0')

from gi.repository import Gio, GLib, Gtk

class GpgKeyList(Gtk.ComboBox):
    def __init__(self):
        Gtk.ComboBox.__init__(self)

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


class MainWindow(Gtk.Window):
    def __init__(self, app):
        Gtk.Window.__init__(self, title="EZ GPG", application = app)

        self.set_border_width(30)
        self.set_position(Gtk.WindowPosition.CENTER)

        gpg_key_combo = GpgKeyList()

        self.add(gpg_key_combo)


class EzGpg(Gtk.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id="org.sgnn7.ezgpg",
                         flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
                         **kwargs)

        GLib.set_application_name("Ez Gpg")
        GLib.set_prgname('EZ GPG')

        self._window = None

    def do_startup(self):
        print("Starting up...")
        Gtk.Application.do_startup(self)

        actions = [
            ('about', self.on_about),
            ('quit', self.on_quit),
        ]

        menu = Gio.Menu()

        for action, callback in actions:
            menu.append(action.capitalize(), "app.%s" % action)

            simple_action = Gio.SimpleAction.new(action, None)
            simple_action.connect('activate', callback)
            self.add_action(simple_action)

        self.set_app_menu(menu)

    def do_activate(self):
        print("Activating...")
        if not self._window:
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
        about_dialog = Gtk.AboutDialog(transient_for=self._window, modal=True)
        about_dialog.present()

    def on_quit(self, action = None, param = None):
        print("Quitting...")
        self._window.destroy()

        self.quit()
