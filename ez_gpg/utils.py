import gi
import gnupg  # Requires python3-gnupg

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk

class EzGpgUtils(object):
    @staticmethod
    def get_gpg_keys():
        gpg = gnupg.GPG()

        keys = []

        for key in gpg.list_keys():
            key_id = key['keyid']
            key_friendly_name = key['uids'][0]

            key_name = "%s %s" % (key_id, key_friendly_name)

            keys.append((key_id, key_name, key_friendly_name))

        keys.sort(key=lambda key_tuple: key_tuple[2])

        return keys

    @staticmethod
    def encrypt_file(window, filename, key_ids):
        dest_filename = "%s.gpg" % filename
        print("Encrypting %s to %s!" % (filename, dest_filename))

        gpg = gnupg.GPG()
        with open(filename, 'rb') as src_file:
                status = gpg.encrypt_file(src_file,
                                          recipients=key_ids,
                                          output=dest_filename)

        print("Encrypted %s to %s!" % (filename, dest_filename))
        EzGpgUtils.show_dialog(window,
                               "Completed!\nFile is at %s" % dest_filename,
                               message_type = Gtk.MessageType.INFO)

    def show_unimplemented_message_box(window):
        EzGpgUtils.show_dialog(window,
                               "This functionality is not yet implemented!",
                               "Not Implemented")

    @staticmethod
    def show_dialog(window, message, title = "EzGpG", message_type = Gtk.MessageType.WARNING):
        dialog = Gtk.MessageDialog(window, 0,
                                   message_type,
                                   Gtk.ButtonsType.OK,
                                   title)
        dialog.format_secondary_text(message)

        response = dialog.run()

        dialog.destroy()
