class Config(object):
    KEY_ID_SIZE = 16

    @staticmethod
    def get_keyservers():
        return [ 'pgp.mit.edu',
                 'keys.gnupg.net',
                 'keyserver.ubuntu.com',
                 'keyserver.opensuse.org' ]
