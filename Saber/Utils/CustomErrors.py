class SaberErrors(Exception):
    pass

    class BadGuildConfiguration(KeyError):
        def __init__(self, message):
            KeyError.__init__(self, message)
