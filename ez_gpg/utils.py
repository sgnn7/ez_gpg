import gi
import gnupg  # Requires python3-gnupg

from os.path import expanduser

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk

class EzGpgUtils(object):
    @staticmethod
    def get_gpg_keyring():
        # TODO: Get this working
        return gnupg.GPG()

    @staticmethod
    def get_gpg_keys(secret = False):
        gpg = EzGpgUtils.get_gpg_keyring()

        keys = []

        for key in gpg.list_keys(secret):
            key_id = key['keyid']

            key_name = key['uids'][0]
            if len(key_name) > 60:
                key_name = key_name[:60] + '...'

            key_friendly_name = "%s %s" % (key_id, key_name)

            keys.append((key_id, key_name, key_friendly_name))

        keys.sort(key=lambda key_tuple: key_tuple[1].lower())

        return keys

    @staticmethod
    def add_gpg_keys_to_combo_box(combo_box, secret = False):
        gpg_keys_list = Gtk.ListStore(str, str)
        for key_id, key_name, key_friendly_name in EzGpgUtils.get_gpg_keys(secret):
            gpg_keys_list.append([key_id, key_name])

        cell = Gtk.CellRendererText()
        combo_box.pack_start(cell, True)
        combo_box.add_attribute(cell, 'text', 1)

        combo_box.set_model(gpg_keys_list)
        combo_box.set_entry_text_column(1)

    @staticmethod
    def encrypt_files(window, filenames, key_ids, use_armor = True, callback = None):
        conversion_list = []
        for filename in filenames:
            dest_filename = "%s.gpg" % filename
            conversion_list.append((filename, dest_filename))

        print(" - Armor:", use_armor)

        gpg = EzGpgUtils.get_gpg_keyring()

        for filename, dest_filename in conversion_list:
            print("Encrypting %s to %s" % (filename, dest_filename))

            with open(filename, 'rb') as src_file:
                status = gpg.encrypt_file(src_file,
                                          recipients=key_ids,
                                          always_trust=True,   # XXX: No key mgmt = no point
                                          armor=use_armor,     # XXX: This doesn't seem to work :(
                                          output=dest_filename)
            print("Status: %s" % status)

            print("Encrypted %s to %s" % (filename, dest_filename))

        # Stop spinner when we return
        if callback:
            callback(window)

        EzGpgUtils.show_dialog(window,
                               "Completed!",
                               message_type = Gtk.MessageType.INFO)

    @staticmethod
    def sign_file(window, filename, key_id, password, use_armor = True, callback = None):
        print(" - Armor:", use_armor)
        # print(" - Password:", password)

        signature_file = "%s.sig" % filename

        print("Signing %s to %s with %s" % (filename, signature_file, key_id))

        gpg = EzGpgUtils.get_gpg_keyring()
        status = None
        with open(filename, 'rb') as src_file:
            status = gpg.sign_file(src_file,
                                   keyid=key_id,
                                   passphrase=password,
                                   detach=True,
                                   output=signature_file)
        print("Status: %s" % status)

        print("Signed %s to %s" % (filename, signature_file))

        # Stop spinner when we return
        if callback:
            callback(window)

        success = True
        dialog_title = "Completed!"
        message_text = "Signature can be found at:\n%s" % signature_file
        message_type = Gtk.MessageType.INFO

        if not status:
            success = False
            dialog_title = "FAILED!"
            message_text = "Unable to sign %s!" % filename
            message_type = Gtk.MessageType.ERROR

        EzGpgUtils.show_dialog(window,
                               message_text,
                               title = dialog_title,
                               message_type = message_type)

        return success

    @staticmethod
    def verify_file(window, source_filename, signature_filename = None):
        gpg = EzGpgUtils.get_gpg_keyring()
        print("Verifying file:", source_filename)

        verification = None

        # XXX: python-gnupg API for this is lame
        if signature_filename:
            with open(signature_filename, 'rb') as sig_file:
                print(" - Verifying with signature: ", signature_filename)
                verification = gpg.verify_file(sig_file, source_filename)
        else:
            with open(source_filename, 'rb') as src_file:
                verification = gpg.verify_file(src_file)

        print(" - Verification data:", verification)
        print(" - Fingerprint:", verification.fingerprint)
        print(" - Username:", verification.username)
        print(" - Key ID:", verification.key_id)

        trust_level = None
        if verification.trust_level:
            print("Trust level:", verification.trust_text)

        dialog_title = "Verified!"
        message_text = "File %s verified!\nTrust = %s" % (source_filename,
                                                         verification.trust_text)
        message_type = Gtk.MessageType.INFO

        if not verification.valid:
            dialog_title = "BAD SIGNATURE!"
            message_text = "Signature for %s was verified and it was bad!" % source_filename
            message_type = Gtk.MessageType.ERROR
        elif not verification.trust_level:
            dialog_title = "NOT VERIFIED!"
            message_text = "Signature for %s CANNOT be verified!\nIt was either not included or was bad!" % source_filename
            message_type = Gtk.MessageType.ERROR
        elif verification.trust_level < verification.TRUST_MARGINAL:
            dialog_title = "NOT TRUSTED ENOGUH!"
            message_text = "Signature for %s was verified but you don't trusit it enough!" % source_filename
            message_type = Gtk.MessageType.ERROR

        EzGpgUtils.show_dialog(window,
                               message_text,
                               title = dialog_title,
                               message_type = message_type)

    @staticmethod
    def check_key_password(key_id, password):
        gpg = EzGpgUtils.get_gpg_keyring()
        signed_data = gpg.sign("check string",
                               keyid=key_id,
                               passphrase=password)

        if str(signed_data):
            print("Password is valid!")
            return True

        # print("Password is NOT valid!")
        return False

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
