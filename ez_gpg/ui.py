import gi
import gnupg  # Requires python3-gnupg

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk

class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="EZ GPG")
        self.connect("delete-event", Gtk.main_quit)

        self.set_border_width(30)

        gpg_keys_list = Gtk.ListStore(str, str)
        for key in self._get_gpg_keys():
            gpg_keys_list.append([key['keyid'], "%s %s" % (key['keyid'], key['uids'][0])])

        gpg_key_combo_box = Gtk.ComboBox.new_with_model_and_entry(gpg_keys_list)
        gpg_key_combo_box.set_entry_text_column(1)

        self.add(gpg_key_combo_box)

    def _get_gpg_keys(self):
        gpg = gnupg.GPG()

        return gpg.list_keys()


class EzGpg(Gtk.Window):
    def launch(self):
        MainWindow().show_all()

        Gtk.main()
