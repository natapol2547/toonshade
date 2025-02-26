import bpy
from typing import List
from mathutils import Vector

class NodeOrganizer:
    created_nodes_names: List[str]

    def __init__(self, material: bpy.types.Material):
        self.node_tree = material.node_tree
        self.nodes = self.node_tree.nodes
        self.links = self.node_tree.links
        self.rightmost = max(
            self.nodes, key=lambda node: node.location.x).location
        self.created_nodes_names = []

    def value_set(self, obj, path, value):
        if '.' in path:
            path_prop, path_attr = path.rsplit('.', 1)
            prop = obj.path_resolve(path_prop)
        else:
            prop = obj
            path_attr = path
        setattr(prop, path_attr, value)

    def create_node(self, node_type, attrs):
        node = self.nodes.new(node_type)
        for attr in attrs:
            self.value_set(node, attr, attrs[attr])
        self.created_nodes_names.append(node.name)
        return node

    def create_link(self, output_node_name: str, input_node_name: str, output_name, input_name):
        output_node = self.nodes[output_node_name]
        input_node = self.nodes[input_node_name]
        self.links.new(input_node.inputs[input_name],
                       output_node.outputs[output_name])

    def move_nodes_offset(self, offset: Vector):
        created_nodes = [self.nodes[name] for name in self.created_nodes_names]
        for node in created_nodes:
            if node.type != 'FRAME':
                node.location += offset

    def move_nodes_to_end(self):
        created_nodes = [self.nodes[name] for name in self.created_nodes_names]
        created_nodes_leftmost = min(
            created_nodes, key=lambda node: node.location.x).location
        offset = self.rightmost - created_nodes_leftmost + Vector((200, 0))
        self.move_nodes_offset(offset)