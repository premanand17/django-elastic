''' Exceptions used in indexing. '''


class LoaderError(Exception):
    ''' Loader error  '''
    def __init__(self, value):
        self.value = value


class MappingError(Exception):
    ''' Mapping error  '''
    def __init__(self, value):
        self.value = value
