import bpy
from bpy.types import Operator
from bpy.utils import register_classes_factory
from bpy.props import StringProperty, PointerProperty, BoolProperty
from .properties import ToonShade
from .nodeOrganizer import NodeOrganizer


class TOONSHADE_OT_ImportNodeTrees(Operator):
    bl_idname = "toonshade.import_nodetrees"
    bl_label = "Import Toon Shade Node Trees"
    bl_description = "Import Toon Shade Node Trees"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ts = ToonShade(context)
        ts.import_ts_node_trees()
        return {'FINISHED'}

# class TOONSHADE_OT_SetupMaterial(Operator):
#     bl_idname = "toonshade.setup_material"
#     bl_label = "Setup Toon Shade Material"
#     bl_description = "Setup Toon Shade Material"
#     bl_options = {'REGISTER', 'UNDO'}

#     def execute(self, context):
#         ts = ToonShade(context)
#         ts.import_ts_node_trees()
#         nodeOrganizer = NodeOrganizer(context.material)
#         nodeOrganizer.create_node('ShaderNodeGroup', {'node_tree': 'ToonShade'})
#         return {'FINISHED'}


class TOONSHADE_OT_ToggleLinkOverride(Operator):
    """Toggle between linked node tree and library override"""
    bl_idname = "toonshade.toggle_link_override"
    bl_label = "Toggle Link/Override"
    bl_options = {'REGISTER', 'UNDO'}
    
    # node_tree_type: StringProperty(
    #     name="Node Tree Type",
    #     description="Type of the node tree (e.g., 'ShaderNodeTree', 'CompositorNodeTree')",
    #     default="ShaderNodeTree"
    # )
    
    node_tree_name: StringProperty(
        name="Node Tree Name",
        description="Name of the node tree to toggle",
        default=""
    )
    
    # @classmethod
    # def poll(cls, context):
    #     return context.space_data and context.space_data.type == 'NODE_EDITOR' and context.space_data.node_tree
    
    def execute(self, context):
        node_tree = bpy.data.node_groups.get(self.node_tree_name)
        
        if not node_tree:
            self.report({'ERROR'}, "No node tree found")
            return {'CANCELLED'}
        
        node_tree.override_library.is_system_override = not node_tree.override_library.is_system_override
        
        # # Check if the node tree is linked or overridden
        # is_linked = node_tree.library is not None and not node_tree.override_library
        # is_override = node_tree.override_library is not None
        
        # if is_linked:
        #     # Create library override
        #     try:
        #         override = bpy.ops.node.make_override_library(id=node_tree.name_full)
        #         self.report({'INFO'}, f"Created library override for '{node_tree.name}'")
        #         return {'FINISHED'}
        #     except Exception as e:
        #         self.report({'ERROR'}, f"Error creating override: {str(e)}")
        #         return {'CANCELLED'}
                
        # elif is_override:
        #     # Remove override and relink
        #     try:
        #         # Get the library path
        #         lib_path = node_tree.override_library.reference.library.filepath
        #         lib_name = node_tree.override_library.reference.name
                
        #         # Remove the override
        #         bpy.ops.node.delete_override_library(id=node_tree.name_full)
                
        #         # Link the original node tree
        #         with bpy.data.libraries.load(lib_path, link=True) as (data_from, data_to):
        #             # Find the node tree in the library
        #             node_tree_type = self.node_tree_type
        #             for nt_name in getattr(data_from, node_tree_type.lower() + "s"):
        #                 if nt_name == lib_name:
        #                     getattr(data_to, node_tree_type.lower() + "s").append(nt_name)
                
        #         self.report({'INFO'}, f"Removed override and relinked '{lib_name}' from library")
        #         return {'FINISHED'}
        #     except Exception as e:
        #         self.report({'ERROR'}, f"Error removing override: {str(e)}")
        #         return {'CANCELLED'}
        # else:
        #     self.report({'WARNING'}, "Selected node tree is not linked or overridden")
        #     return {'CANCELLED'}

class TOONSHADE_OT_AddNodeTree(Operator):
    bl_idname = "toonshade.add_node_tree"
    bl_label = "Add Toon Shade Nodetree"
    bl_description = "Add Toon Shade Nodetree"
    bl_options = {'REGISTER', 'UNDO'}
    
    node_tree_name: StringProperty(
        name="Node Tree Name",
        description="Name of the node tree to add the node to",
        default=""
    )
    
    link: BoolProperty(
        name="Link",
        description="Link the node tree",
        default=False
    )

    def execute(self, context):
        ts = ToonShade(context)
        node_tree = ts.get_nodetree_from_library(self.node_tree_name, force_reload=False, link=self.link)
        if not node_tree:
            self.report({'ERROR'}, "No node tree found")
            return {'CANCELLED'}
        bpy.ops.node.add_node('INVOKE_DEFAULT',
                              use_transform=True,
                              settings=[{"name": "node_tree", "value": f"bpy.data.node_groups['{self.node_tree_name}']"}],
                              type = "ShaderNodeGroup"
                              )
        return {'FINISHED'}

classes = (
    TOONSHADE_OT_ImportNodeTrees,
    TOONSHADE_OT_ToggleLinkOverride,
    TOONSHADE_OT_AddNodeTree,
)

register, unregister = register_classes_factory(classes)