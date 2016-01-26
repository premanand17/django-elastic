''' Used to create the mapping properties for an index. '''
from elastic.management.loaders.exceptions import MappingError


class MappingProperties():
    ''' Build the mapping properties for an index. '''

    # context suggester
    CONTEXT_SUGGESTER = {
        "auth": {
            "type": "category",
            "path": "group_name",
            "default": ["public"]
        }
    }

    def __init__(self, idx_type, parent=None):
        ''' For a given index type create the mapping properties. '''
        self.idx_type = idx_type
        self.mapping_properties = {self.idx_type: {"properties": {}}}
        if parent is not None:
            self.mapping_properties[self.idx_type].update({"_parent": {"type": parent}})
        self.column_names = []

    def add_property(self, name, map_type, index=None, analyzer=None,
                     index_analyzer=None, search_analyzer=None,
                     property_format=None, index_options=None, **kwargs):
        ''' Add a property to the mapping. '''
        self.mapping_properties[self.idx_type]["properties"][name] = {"type": map_type}
        if index is not None:
            self.mapping_properties[self.idx_type]["properties"][name].update({"index": index})

        if analyzer is not None:
            self.mapping_properties[self.idx_type]["properties"][name].update({"analyzer": analyzer})
        if index_analyzer is not None:
            self.mapping_properties[self.idx_type]["properties"][name].update({"index_analyzer": index_analyzer})
        if search_analyzer is not None:
            self.mapping_properties[self.idx_type]["properties"][name].update({"search_analyzer": search_analyzer})

        if property_format is not None:
            self.mapping_properties[self.idx_type]["properties"][name].update({"format": property_format})
        if index_options is not None:
            self.mapping_properties[self.idx_type]["properties"][name].update({"index_options": index_options})

        for key in kwargs:
            self.mapping_properties[self.idx_type]["properties"][name].update({key: kwargs[key]})

        self.column_names.append(name)
        return self

    def add_properties(self, mapping_properties):
        ''' Add a nested set of properties to the mapping. '''
        if not isinstance(mapping_properties, MappingProperties):
            raise MappingError("not a MappingProperties")
        self.mapping_properties[self.idx_type]["properties"].update(mapping_properties.mapping_properties)
        return self

    def get_column_names(self):
        return self.column_names
