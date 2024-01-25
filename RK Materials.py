bl_info = {
    "name": "RK Materials",
    "category": "Import-Export",
    "author": "A Sagar",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > Tools Tab",
    "description": "Imports materials from another .blend file",
    "warning": "",
    "wiki_url": "",
}

import bpy

class MaterialItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Material Name")
    filepath: bpy.props.StringProperty(name="File Path")

class ImportMaterialsOperator(bpy.types.Operator):
    """Import Materials"""
    bl_idname = "import_materials.operator"
    bl_label = "Import Materials"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    excluded_keywords = ['lights']  # List of keywords to exclude

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        context.scene.loading_materials = True

        if not self.filepath.lower().endswith('.blend'):
            self.report({'ERROR'}, "Not a .blend file")
            context.scene.loading_materials = False
            return {'CANCELLED'}

        with bpy.data.libraries.load(self.filepath, link=False) as (data_from, data_to):
            materials = [mat for mat in data_from.materials if not any(keyword in mat.lower() for keyword in self.excluded_keywords)]

        imported_materials = context.scene.imported_materials
        imported_materials.clear()
        for mat_name in materials:
            item = imported_materials.add()
            item.name = mat_name
            item.filepath = self.filepath

        self.report({'INFO'}, "Material names loaded")
        context.scene.loading_materials = False
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class ApplyMaterialOperator(bpy.types.Operator):
    """Apply Material"""
    bl_idname = "apply_material.operator"
    bl_label = "Apply Material"
    bl_options = {'REGISTER', 'UNDO'}

    material_name: bpy.props.StringProperty()
    material_file: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        with bpy.data.libraries.load(self.material_file, link=False) as (data_from, data_to):
            if self.material_name in data_from.materials:
                data_to.materials = [self.material_name]

        material = bpy.data.materials.get(self.material_name)
        if material:
            if context.object.data.materials:
                context.object.data.materials[0] = material
            else:
                context.object.data.materials.append(material)
            self.report({'INFO'}, f"Material {material.name} applied")
        else:
            self.report({'ERROR'}, "Material not found in the file")
        return {'FINISHED'}

class ImportMaterialsPanel(bpy.types.Panel):
    """Creates a Panel in the 3D View's Tools Tab"""
    bl_label = "RK Materials"
    bl_idname = "IMPORT_RK_materials"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'RK Materials'

    def draw(self, context):
        layout = self.layout
        layout.operator(ImportMaterialsOperator.bl_idname)

        if context.scene.loading_materials:
            layout.label(text="Loading...", icon='INFO')
        else:
            for item in context.scene.imported_materials:
                row = layout.row()
                row.label(text=item.name)
                op = row.operator(ApplyMaterialOperator.bl_idname, text="Apply")
                op.material_name = item.name
                op.material_file = item.filepath

def register():
    bpy.utils.register_class(MaterialItem)
    bpy.utils.register_class(ImportMaterialsOperator)
    bpy.utils.register_class(ApplyMaterialOperator)
    bpy.utils.register_class(ImportMaterialsPanel)
    bpy.types.Scene.imported_materials = bpy.props.CollectionProperty(type=MaterialItem)
    bpy.types.Scene.loading_materials = bpy.props.BoolProperty(default=False)

def unregister():
    del bpy.types.Scene.imported_materials
    del bpy.types.Scene.loading_materials
    bpy.utils.unregister_class(MaterialItem)
    bpy.utils.unregister_class(ImportMaterialsOperator)
    bpy.utils.unregister_class(ApplyMaterialOperator)
    bpy.utils.unregister_class(ImportMaterialsPanel)

if __name__ == "__main__":
    register()
