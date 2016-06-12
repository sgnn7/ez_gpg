import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk

class EzGpg:
    def launch(self):
        window = Gtk.Window()

        window.connect("delete-event", Gtk.main_quit)
        window.set_title("EZ GPG")

        window.show_all()

        Gtk.main()
