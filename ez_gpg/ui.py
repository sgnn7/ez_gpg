import gi
import gnupg  # Requires python3-gnupg

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk

class GpgKeyList(Gtk.ComboBox):
    def __init__(self):
        Gtk.ComboBox.__init__(self)

        gpg_keys_list = Gtk.ListStore(str, str)
        for key in self._get_gpg_keys():
            key_id = key['keyid']
            key_name = "%s %s" % (key['keyid'], key['uids'][0])

            gpg_keys_list.append([key_id, key_name])

        cell = Gtk.CellRendererText()
        self.pack_start(cell, True)
        self.add_attribute(cell, 'text', 1)

        self.set_model(gpg_keys_list)
        self.set_entry_text_column(1)

    def _get_gpg_keys(self):
        gpg = gnupg.GPG()

        return gpg.list_keys()


class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="EZ GPG")
        self.connect("delete-event", Gtk.main_quit)

        self.set_border_width(30)
        self.set_position(Gtk.WindowPosition.CENTER)

        gpg_key_combo = GpgKeyList()

        self.add(gpg_key_combo)


class EzGpg(Gtk.Window):
    def launch(self):
        MainWindow().show_all()

        Gtk.main()
