import bpy
from bpy.types import Menu

import sys
dev_path = '/home/feral/engineering/addon_workshop/softops'
sys.path.insert(1, dev_path)


class _MT_RigFiberMenu(Menu):
    bl_label = "Rig Fiber"
    bl_options = {'REGISTER'}

    def draw(self, context):
        layout = self.layout

        pie = layout.menu_pie()
        pie.operator('rigging.muscle_c_fiber_from_active')
        pie.operator("rigging.muscle_s_fiber_from_active")
        pie.operator("rigging.muscle_double_fiber_from_active")
        pie.operator("rigging.adjust_fiber_bend")


class CallRigFiberPieMenu(bpy.types.Operator):
    """Calls a rig fiber creation pie menu"""
    bl_idname = "rigging.call_rig_fiber_menu"
    bl_label = "Call Rig Fiber Pie Menu"
    bl_options = {'REGISTER'}

    def execute(self, context):
        bpy.ops.wm.call_menu_pie(name="_MT_RigFiberMenu")

        return {'FINISHED'}


class _MT_InstallMuscleMenu(Menu):
    bl_label = "Install Muscle"
    bl_options = {'REGISTER'}

    def draw(self, context):
        layout = self.layout

        pie = layout.menu_pie()
        pie.operator('rigging.install_fusiform_muscle')
        pie.operator("rigging.install_wide_muscle")
        pie.operator("rigging.stretch_to_rig_from_active")
        pie.operator("rigging.bbone_from_stretch_to")
        pie.operator("rigging.adjust_bbone_rig")


class CallInstallMusclePieMenu(bpy.types.Operator):
    """Calls a muscle instalation pie menu"""
    bl_idname = "rigging.call_install_muscle_menu"
    bl_label = "Call Install Muscle Pie Menu"
    bl_options = {'REGISTER'}

    def execute(self, context):
        bpy.ops.wm.call_menu_pie(name="_MT_InstallMuscleMenu")

        return {'FINISHED'}



class _MT_BezierSurfaceMenu(Menu):
    bl_label = "Bezier Surface"
    bl_options = {'REGISTER'}

    def draw(self, context):
        layout = self.layout

        pie = layout.menu_pie()
        # pie.operator('object.install_bezier_surface__uniform_num')
        # pie.operator('object.install_bezier_surface__adaptive_num')
        # pie.operator('object.install_bezier_surface__uniform_sym')
        # pie.operator('object.install_bezier_surface__adaptive_sym')
        pie.operator("object.install_bezier_surface__uniform_num__aa")
        pie.operator("object.install_bezier_surface__adaptive_num__aa")


class CallBezierSurfacePieMenu(bpy.types.Operator):
    """Calls a bezier surface generator pie menu"""
    bl_idname = "object.call_bezier_surface_menu"
    bl_label = "Call Bezier Surface Pie Menu"
    bl_options = {'REGISTER'}

    def execute(self, context):
        bpy.ops.wm.call_menu_pie(name="_MT_BezierSurfaceMenu")

        return {'FINISHED'}



class _MT_BendTargetSelectMenu(Menu):
    bl_label = "Bend Target Select"
    bl_options = {'REGISTER'}

    def draw(self, context):
        layout = self.layout

        pie = layout.menu_pie()
        pie.operator('rigging.select_all_pose_bend_targets')
        pie.operator('rigging.select_bend_targets_within_fiber')
        pie.operator("rigging.clear_bend_target_user_transforms")
        # pie.operator("rigging.place_bend_targets_on_fiber")


class CallBendTargetSelectPieMenu(bpy.types.Operator):
    """Calls the bend target selection pie menu"""
    bl_idname = "object.call_bend_target_select_menu"
    bl_label = "Call Bend Target Select Pie Menu"
    bl_options = {'REGISTER'}

    def execute(self, context):
        bpy.ops.wm.call_menu_pie(name="_MT_BendTargetSelectMenu")

        return {'FINISHED'}




class _MT_SplineSelectMenu(Menu):
    bl_label = "Spline Select"
    bl_options = {'REGISTER'}

    def draw(self, context):
        layout = self.layout

        pie = layout.menu_pie()
        pie.operator('object.select_splines__from_active')
        pie.operator('object.select_transversal_splines__from_active')
        pie.operator('object.select_longitudinal_splines__from_active')
        pie.operator('object.select_transversal_handle_splines__from_active')
        pie.operator('object.select_longitudinal_handle_splines__from_active')
        pie.operator('object.select_transversal_core_splines__from_active')
        pie.operator('object.select_longitudinal_core_splines__from_active')
        pie.operator('object.select_column__from_active')

class CallSplineSelectPieMenu(bpy.types.Operator):
    """Calls the spline selection pie menu"""
    bl_idname = "object.call_spline_select_menu"
    bl_label = "Call Spline Select Pie Menu"
    bl_options = {'REGISTER'}

    def execute(self, context):
        bpy.ops.wm.call_menu_pie(name="_MT_SplineSelectMenu")

        return {'FINISHED'}




class _MT_ConformSplineMenu(Menu):
    bl_label = "Conform Spline"
    bl_options = {'REGISTER'}

    def draw(self, context):
        layout = self.layout

        pie = layout.menu_pie()
        pie.operator('object.conform_long_splines_to_transversal_from_active')
        pie.operator('object.conform_trans_splines_to_longitudinal_from_active')
        pie.operator('object.conform_long_handles_to_transversal_from_active')
        pie.operator('object.conform_trans_handles_to_longitudinal_from_active')
        pie.operator('object.conform_long_cores_to_transversal_from_active')
        pie.operator('object.conform_trans_cores_to_longitudinal_from_active')


class CallConformSplinePieMenu(bpy.types.Operator):
    """Calls the conform spline pie menu"""
    bl_idname = "object.call_conform_spline_menu"
    bl_label = "Call Conform Spline Pie Menu"
    bl_options = {'REGISTER'}

    def execute(self, context):
        bpy.ops.wm.call_menu_pie(name="_MT_ConformSplineMenu")

        return {'FINISHED'}



class _MT_InstallSplineMenu(Menu):
    bl_label = "Install Spline"
    bl_options = {'REGISTER'}

    def draw(self, context):
        layout = self.layout

        pie = layout.menu_pie()
        pie.operator('object.install_missing_longitudinal_handles')
        pie.operator('object.install_missing_transversal_handles')


class CallInstallSplinePieMenu(bpy.types.Operator):
    """Calls the install spline pie menu"""
    bl_idname = "object.call_install_spline_menu"
    bl_label = "Call Install Spline Pie Menu"
    bl_options = {'REGISTER'}

    def execute(self, context):
        bpy.ops.wm.call_menu_pie(name="_MT_InstallSplineMenu")

        return {'FINISHED'}



class _MT_SymmetrizeSilhuetteMenu(Menu):
    bl_label = "Symmetrize Silhuette"
    bl_options = {'REGISTER'}

    def draw(self, context):
        layout = self.layout

        pie = layout.menu_pie()
        pie.operator('object.symmetrize_silhuette_neg_x')
        pie.operator('object.symmetrize_silhuette_pos_x')
        pie.operator('object.symmetrize_silhuette_neg_y')
        pie.operator('object.symmetrize_silhuette_pos_y')
        pie.operator('object.symmetrize_silhuette_neg_z')
        pie.operator('object.symmetrize_silhuette_pos_z')


class CallSymmetrizeSilhuetteMenu(bpy.types.Operator):
    """Calls the symmetrize silhuette pie menu"""
    bl_idname = "object.call_symmetrize_silhuette_menu"
    bl_label = "Call Symmetrize Silhuette Pie Menu"
    bl_options = {'REGISTER'}

    def execute(self, context):
        bpy.ops.wm.call_menu_pie(name="_MT_SymmetrizeSilhuetteMenu")

        return {'FINISHED'}







keyless_op_data = []

keyless_op_data.append({
    'class': _MT_RigFiberMenu,
})
keyless_op_data.append({
    'class': _MT_InstallMuscleMenu,
})
keyless_op_data.append({
    'class': _MT_BezierSurfaceMenu,
})
keyless_op_data.append({
    'class': _MT_BendTargetSelectMenu,
})
keyless_op_data.append({
    'class': _MT_SplineSelectMenu,
})
keyless_op_data.append({
    'class': _MT_ConformSplineMenu,
})
keyless_op_data.append({
    'class': _MT_InstallSplineMenu,
})
keyless_op_data.append({
    'class': _MT_SymmetrizeSilhuetteMenu,
})



operator_data = []

operator_data.append({
    'class': CallRigFiberPieMenu,
    'keymap': 'G',
    'ctrl': True,
    'alt': True,
    'shift': False,
})

operator_data.append({
    'class': CallInstallMusclePieMenu,
    'keymap': 'R',
    'ctrl': True,
    'alt': True,
    'shift': False,
})

operator_data.append({
    'class': CallBezierSurfacePieMenu,
    'keymap': 'E',
    'ctrl': False,
    'alt': True,
    'shift': True,
})

operator_data.append({
    'class': CallBendTargetSelectPieMenu,
    'keymap': 'E',
    'ctrl': True,
    'alt': True,
    'shift': False,
})

operator_data.append({
    'class': CallSplineSelectPieMenu,
    'keymap': 'D',
    'ctrl': False,
    'alt': True,
    'shift': True,
})

operator_data.append({
    'class': CallConformSplinePieMenu,
    'keymap': 'C',
    'ctrl': False,
    'alt': True,
    'shift': True,
})

operator_data.append({
    'class': CallInstallSplinePieMenu,
    'keymap': 'X',
    'ctrl': False,
    'alt': True,
    'shift': True,
})

operator_data.append({
    'class': CallSymmetrizeSilhuetteMenu,
    'keymap': 'Q',
    'ctrl': False,
    'alt': True,
    'shift': True,
})
