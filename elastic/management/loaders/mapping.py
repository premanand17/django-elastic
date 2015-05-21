''' Used to create the mapping properties for an index. '''
from elastic.management.loaders.exceptions import MappingError


class MappingProperties():
    ''' Build the mapping properties for an index. '''

    def __init__(self, idx_type):
        ''' For a given index type create the mapping properties. '''
        self.idx_type = idx_type
        self.mapping_properties = {self.idx_type: {"properties": {}}}
        self.column_names = []

    def add_property(self, name, map_type, index=None, analyzer=None, property_format=None):
        ''' Add a property to the mapping. '''
        self.mapping_properties[self.idx_type]["properties"][name] = {"type": map_type}
        if index is not None:
            self.mapping_properties[self.idx_type]["properties"][name].update({"index": index})
        if analyzer is not None:
            self.mapping_properties[self.idx_type]["properties"][name].update({"analyzer": analyzer})
        if property_format is not None:
            self.mapping_properties[self.idx_type]["properties"][name].update({"format": property_format})
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
