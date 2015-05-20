

class LoaderError(Exception):
    ''' Loader error  '''
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class MappingError(Exception):
    ''' Mapping error  '''
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
