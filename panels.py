import bpy
from bpy.utils import register_classes_factory
from .properties import ToonShade, TS_NODETREE_NAMES
from . import addon_updater_ops
from .common import find_node

@addon_updater_ops.make_annotations
class ToonShadePreferences(bpy.types.AddonPreferences):
	"""Demo bare-bones preferences"""
	bl_idname = __package__

	# Addon updater preferences.

	auto_check_update = bpy.props.BoolProperty(
		name="Auto-check for Update",
		description="If enabled, auto-check for updates using an interval",
		default=False)

	updater_interval_months = bpy.props.IntProperty(
		name='Months',
		description="Number of months between checking for updates",
		default=0,
		min=0)

	updater_interval_days = bpy.props.IntProperty(
		name='Days',
		description="Number of days between checking for updates",
		default=7,
		min=0,
		max=31)

	updater_interval_hours = bpy.props.IntProperty(
		name='Hours',
		description="Number of hours between checking for updates",
		default=0,
		min=0,
		max=23)

	updater_interval_minutes = bpy.props.IntProperty(
		name='Minutes',
		description="Number of minutes between checking for updates",
		default=0,
		min=0,
		max=59)

	def draw(self, context):
		layout = self.layout

		# Works best if a column, or even just self.layout.
		mainrow = layout.row()
		col = mainrow.column()

		# Updater draw function, could also pass in col as third arg.
		addon_updater_ops.update_settings_ui(self, context)

		# Alternate draw function, which is more condensed and can be
		# placed within an existing draw function. Only contains:
		#   1) check for update/update now buttons
		#   2) toggle for auto-check (interval will be equal to what is set above)
		# addon_updater_ops.update_settings_ui_condensed(self, context, col)

		# Adding another column to help show the above condensed ui as one column
		# col = mainrow.column()
		# col.scale_y = 2
		# ops = col.operator("wm.url_open","Open webpage ")
		# ops.url=addon_updater_ops.updater.website


class ToonShadePanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Toon Shade"
    bl_idname = "OBJECT_PT_toonshade"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Toon Shade'

    def draw(self, context):
        layout = self.layout

        ts = ToonShade(context)
        
        col = layout.column()
        col.scale_y = 1.5
        # if not ts.check_ts_node_trees():
        #     col.operator("toonshade.import_nodetrees", icon='IMPORT', text="Import Toon Shade")
        #     return
        for tree_name in TS_NODETREE_NAMES:
            ops = col.operator("toonshade.add_node_tree", text=f"Add {tree_name}", icon='NODE_MATERIAL').node_tree_name = tree_name
            # ops = col.operator("node.add_node", text=f"Add {tree_name}", icon='NODE_MATERIAL')
            # ops.use_transform=True
            # ops.settings=[{"name": "node_tree", "value": f"bpy.data.node_groups['{tree_name}']"}]
            # ops.type = "ShaderNodeGroup"
        ts_nodes = ts.get_toonshade_nodes()
        if not ts_nodes:
            layout.label(text="Toon Shade is not connected")
            return
        col.separator()
        layout.label(text="Environment Settings:")
        box = layout.box()
        col = box.column()
        col.scale_y = 1.5
        col.prop(ts.settings, "time_of_day")
        
        goo_nodetree = bpy.data.node_groups.get("Toon Shade Goo")
        if not goo_nodetree:
            return
        colorramp_node = find_node(goo_nodetree, {"name": "Toon Shade Color Ramp"})
        if goo_nodetree.library:
            box.label(text="Node is linked to a library")
        else:
            if colorramp_node:
                box.label(text="Time of Day Colors:")
                box.template_node_inputs(colorramp_node)
        
        layout.label(text="Shader Settings:")
        for ts_node in ts_nodes:
            box = layout.box()
            box.template_node_inputs(ts_node)


classes = (
    ToonShadePreferences,
    ToonShadePanel,
)

register, unregister = register_classes_factory(classes)