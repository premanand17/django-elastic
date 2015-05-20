''' Used to define analyzers in the mapping. '''


class Analyzer:
    ''' See L{Custom Analyzers<www.elastic.co/guide/en/elasticsearch/guide/master/custom-analyzers.html>}. '''

    def __init__(self, name, char_filter=None, tokenizer='standard', token_filters='standard'):
        analyzer = {name: {}}
        if tokenizer is not None:
            analyzer[name]['tokenizer'] = tokenizer
        if token_filters is not None:
            analyzer[name]['filter'] = token_filters
        self.analyzer = {"analysis": {"analyzer": analyzer}}
