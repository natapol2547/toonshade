import bpy
from bpy.types import NodeTree, PropertyGroup, Context
from bpy.props import FloatProperty, PointerProperty
from .common import get_addon_filepath, get_connected_nodes, get_active_material_output

LIBRARY_FILE_NAME = "library.blend"
TS_NODETREE_NAMES = [
    "Toon Shade Goo",
    "Environment Color",
    "Color Blender",
    ]

def cleanup_duplicate_nodegroups(node_tree: NodeTree):
    """
    Cleanup duplicate node groups by using Blender's remap_users feature.
    This automatically handles all node links and nested node groups.

    Args:
        node_group_name (str): Name of the main node group to clean up
    """
    def find_original_nodegroup(name):
        # Get the base name by removing the .001, .002 etc. if present
        # This gets the part before the first dot
        base_name = name.split('.')[0]

        # Find all matching node groups
        matching_groups = [ng for ng in bpy.data.node_groups
                           if ng.name == base_name or ng.name.split('.')[0] == base_name]

        if not matching_groups:
            return None

        # The original is likely the one without a number suffix
        # or the one with the lowest number if all have suffixes
        for ng in matching_groups:
            if ng.name == base_name:  # Exact match without any suffix
                return ng

        # If we didn't find an exact match, return the one with lowest suffix number
        return sorted(matching_groups, key=lambda x: x.name)[0]

    # Get active Group output node
    def get_active_group_output_node(node_tree):
        for node in node_tree.nodes:
            if node.type == 'GROUP_OUTPUT' and node.is_active_output:
                return node
        return None
    
    active_output_node = get_active_group_output_node(node_tree)
    if not active_output_node:
        return

    # Process each node group
    for node in get_connected_nodes(active_output_node):
        # print(f"Checking node: {node.name}")
        if node.type == 'GROUP' and node.node_tree:
            ng = node.node_tree

            # Find the original node group
            original_group = find_original_nodegroup(ng.name)

            # If this is a duplicate (not the original) and we found the original
            if original_group and ng != original_group and ng.name.startswith(original_group.name):
                print(f"Cleaning up duplicate node group: {ng.name}")
                # Remap all users of this node group to the original
                ng.user_remap(original_group)
                # Remove the now-unused node group
                bpy.data.node_groups.remove(ng)

class ToonShade():
    def __init__(self, context: Context):
        self.context = context
        self.settings = context.view_layer.toon_shade
        self.object = context.object
        self.material = self.object.active_material if self.object else None
        self.node_tree = self.material.node_tree if self.material else None
        self.time_of_day = float(self.settings.time_of_day)
        
    def check_ts_node_trees(self):
        # Check if the node group already exists
        for tree_name in TS_NODETREE_NAMES:
            nt = bpy.data.node_groups.get(tree_name)
            if not nt:
                return False
        return True
    
    def import_ts_node_trees(self):
        for tree_name in TS_NODETREE_NAMES:
            self.get_nodetree_from_library(tree_name, force_reload=True, link=True)
    
    def get_nodetree_from_library(self, tree_name, force_reload=False, link=False) -> NodeTree:
        print(f"Loading node group: {tree_name}")
        # Check if the node group already exists
        nt = bpy.data.node_groups.get(tree_name)
        old_nt = None
        if nt:
            if not force_reload:
                return nt
            old_nt = nt.copy()

        # Load the library file
        filepath = get_addon_filepath() + LIBRARY_FILE_NAME
        with bpy.data.libraries.load(filepath, link=link) as (lib_file, current_file):
            lib_node_group_names = lib_file.node_groups
            current_node_groups_names = current_file.node_groups
            for node_group_name in lib_node_group_names:
                if node_group_name == tree_name:
                    current_node_groups_names.append(node_group_name)
        
        # Getting the node group
        nt = bpy.data.node_groups.get(tree_name)
        if not nt:
            return None
        
        # Find all node groups with the same base name
        matching_groups = [ng for ng in bpy.data.node_groups 
                  if ng.name == tree_name or ng.name.startswith(tree_name + ".")]
        
        if len(matching_groups) > 1:
            # Sort by suffix number - those without a suffix are considered version 0
            def get_suffix_number(ng):
                if ng.name == tree_name:
                    return 0
                parts = ng.name.split(".")
                if len(parts) > 1:
                    try:
                        return int(parts[-1])
                    except ValueError:
                        return 0
                return 0
            
            sorted_groups = sorted(matching_groups, key=get_suffix_number)
            
            # Get the latest version (highest suffix)
            latest_version = sorted_groups[-1]
            
            # Remap all older versions to the latest one
            for old_ng in sorted_groups[:-1]:
                cleanup_duplicate_nodegroups(old_ng)
                print(f"Remapping users from {old_ng.name} to {latest_version.name}")
                old_ng.user_remap(latest_version)
                bpy.data.node_groups.remove(old_ng)
            
            # Use the latest version
            nt = latest_version
        
        # Ensure the node group has the correct name (without suffix)
        if nt.name != tree_name:
            nt.name = tree_name
        
        if not link:
            # Rename the new node group
            nt.name = tree_name
            nt.use_fake_user = True
            cleanup_duplicate_nodegroups(nt)
        return nt
    
    def get_toonshade_nodes(self):
        obj = self.context.object
        if not obj:
            return None
        mat = obj.active_material
        if not mat:
            return None
        output_node = get_active_material_output(mat.node_tree)
        if not output_node:
            return None
        nodes = get_connected_nodes(output_node)
        toonshade_nodes = []
        for node in nodes:
            if hasattr(node, "node_tree") and node.node_tree.name in TS_NODETREE_NAMES:
                toonshade_nodes.append(node)
        return toonshade_nodes


class ToonShadeProperties(PropertyGroup):
    time_of_day: FloatProperty(
        name="Time of Day",
        description="Time of Day",
        default=0.0,
        unit='TIME',
    )


def register():
    bpy.utils.register_class(ToonShadeProperties)
    bpy.types.ViewLayer.toon_shade = PointerProperty(type=ToonShadeProperties)

def unregister():
    del bpy.types.ViewLayer.toon_shade
    bpy.utils.unregister_class(ToonShadeProperties)