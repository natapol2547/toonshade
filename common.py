import bpy
from bpy.types import Node, NodeTree
import os
from typing import List

def get_addon_filepath():
    return os.path.dirname(bpy.path.abspath(__file__)) + os.sep

def find_node_tree(tree_name) -> bpy.types.NodeTree:
    nt = bpy.data.node_groups.get(tree_name)
    return nt

def get_active_material_output(node_tree: NodeTree) -> Node:
    """Get the active material output node

    Args:
        node_tree (bpy.types.NodeTree): The node tree to check

    Returns:
        bpy.types.Node: The active material output node
    """
    for node in node_tree.nodes:
        if node.bl_idname == "ShaderNodeOutputMaterial" and node.is_active_output:
            return node
    return None

def get_connected_nodes(output_node: Node) -> List[Node]:
    """
    Gets all nodes connected to the given output_node, 
    maintaining the order in which they were found and removing duplicates.

    Args:
        node: The output node.

    Returns:
        A list of nodes, preserving the order of discovery and removing duplicates.
    """

    nodes = []
    visited = set()  # Here's where the set is used

    def traverse(node: Node):
        if node not in visited:  # Check if the node has been visited
            visited.add(node)  # Add the node to the visited set
            nodes.append(node)
            if hasattr(node, 'node_tree') and node.node_tree:
                for sub_node in node.node_tree.nodes:
                    traverse(sub_node)
            for input in node.inputs:
                for link in input.links:
                    traverse(link.from_node)

    traverse(output_node)
    return nodes

def find_node(node_tree, node_details):
    if not node_tree:
        return None
    for node in node_tree.nodes:
        match = True
        for key, value in node_details.items():
            if getattr(node, key) != value:
                match = False
                break
        if match:
            return node
    return None