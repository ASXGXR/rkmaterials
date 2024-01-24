bl_info = {
    "name": "Import Materials",
    "author": "A Sagar",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > Tools Tab",
    "description": "Imports materials from another .blend file",
    "warning": "",
    "wiki_url": "",
    "category:": "RK Materials"
}

import bpy
import json
from urllib import request

class MaterialItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Material Name")

class ImportMaterialsOperator(bpy.types.Operator):
    """Import Materials"""
    bl_idname = "import_materials.operator"
    bl_label = "Import Materials"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        if not self.filepath.lower().endswith('.blend'):
            self.report({'ERROR'}, "Not a .blend file")
            return {'CANCELLED'}

        # Extract words from the filename
        filename = bpy.path.basename(self.filepath)
        filename_without_extension = bpy.path.display_name_from_filepath(filename)
        title_words = set(filename_without_extension.split())

        with bpy.data.libraries.load(self.filepath, link=False) as (data_from, data_to):
            # Import materials containing words from the title
            data_to.materials = [mat for mat in data_from.materials if any(word.lower() in mat.lower() for word in title_words)]

        imported_materials = context.scene.imported_materials
        imported_materials.clear()
        for mat in data_to.materials:
            item = imported_materials.add()
            item.name = mat.name
        self.report({'INFO'}, "Materials imported successfully")
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

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        material = bpy.data.materials.get(self.material_name)
        if material:
            if context.object.data.materials:
                context.object.data.materials[0] = material
            else:
                context.object.data.materials.append(material)
            self.report({'INFO'}, f"Material {material.name} applied")
        else:
            self.report({'ERROR'}, f"Material {self.material_name} not found")
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

        for item in context.scene.imported_materials:
            row = layout.row()
            row.label(text=item.name)
            op = row.operator(ApplyMaterialOperator.bl_idname, text="Apply")
            op.material_name = item.name

def check_for_update():
    current_version = bl_info['version']
    url = "https://api.github.com/repos/your_username/your_repository/releases/latest"
    try:
        with request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            latest_version = tuple(map(int, data['tag_name'].split('.')))
            return latest_version > current_version
    except Exception as e:
        print("Error checking for update:", e)
        return False

update_available = False

def register():
    global update_available
    update_available = check_for_update()
    bpy.utils.register_class(MaterialItem)
    bpy.types.Scene.imported_materials = bpy.props.CollectionProperty(type=MaterialItem)
    bpy.utils.register_class(ImportMaterialsOperator)
    bpy.utils.register_class(ApplyMaterialOperator)
    bpy.utils.register_class(ImportMaterialsPanel)

class UpdateCheckPanel(bpy.types.Panel):
    bl_label = "Addon Update Check"
    bl_idname = "UPDATE_PT_check"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tools'

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        if update_available:
            row.label(text="Update available!", icon='INFO')
            row.operator("wm.url_open", text="Download Update").url = "https://github.com/ASXGXR/rkmaterials/releases"
        else:
            row.label(text="Addon is up to date", icon='CHECKMARK')

def unregister():
    del bpy.types.Scene.imported_materials
    bpy.utils.unregister_class(MaterialItem)
    bpy.utils.unregister_class(ImportMaterialsOperator)
    bpy.utils.unregister_class(ApplyMaterialOperator)
    bpy.utils.unregister_class(ImportMaterialsPanel)

if __name__ == "__main__":
    register()
