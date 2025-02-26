import bpy
from bpy.types import NodeTree, PropertyGroup, Context
from bpy.props import FloatProperty, PointerProperty
from .common import get_addon_filepath, get_connected_nodes, get_active_material_output

LIBRARY_FILE_NAME = "library.blend"
TS_NODETREE_NAMES = [
    "Toon Shade Goo",
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

    # Process each node group
    for node in node_tree.nodes:
        if node.type == 'GROUP' and node.node_tree:
            ng = node.node_tree

            # Find the original node group
            original_group = find_original_nodegroup(ng.name)

            # If this is a duplicate (not the original) and we found the original
            if original_group and ng != original_group:
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
            old_nt = nt

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
        cleanup_duplicate_nodegroups(nt)
        
        # Remap user of the old node group
        if old_nt:
            nt.user_remap(old_nt)
            bpy.data.node_groups.remove(old_nt)
        
        if not link:
            # Rename the new node group
            nt.name = tree_name
            nt.use_fake_user = True
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