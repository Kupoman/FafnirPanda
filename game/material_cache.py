import ctypes

import panda3d.core as p3d


class MaterialCache:
    def __init__(self):
        self.max_material_count = -1
        self.cache_texture = p3d.Texture()
        self.count_texture = p3d.Texture()
        self.count_texture.set_clear_color(p3d.LColor(0.0, 0.0, 0.0, 0.0))
        self.ensure_size(0)

    def ensure_size(self, material_count):
        if material_count > self.max_material_count:
            self.max_material_count = material_count
            self.cache_texture.setup_buffer_texture(
                self.max_material_count,
                p3d.Texture.T_unsigned_byte,
                p3d.Texture.F_rgba8,
                p3d.GeomEnums.UH_dynamic
            )
            self.count_texture.setup_buffer_texture(
                self.max_material_count,
                p3d.Texture.T_int,
                p3d.Texture.F_r32i,
                p3d.GeomEnums.UH_dynamic
            )

    def update(self, material_list, np_list):
        if len(material_list) == 0:
            print('Warning: Material list is empty')
            return

        self.ensure_size(len(material_list))
        ram_size = len(material_list) * 4
        ram_image = (ctypes.c_byte * ram_size)()
        material_map = {}
        for i, material in enumerate(material_list):
            material_map[material.name] = i
            diffuse_color = material.get_diffuse()
            image_idx = i * 4
            ram_image[image_idx + 0] = int(diffuse_color.x * 255)
            ram_image[image_idx + 1] = int(diffuse_color.y * 255)
            ram_image[image_idx + 2] = int(diffuse_color.z * 255)
            ram_image[image_idx + 3] = int(diffuse_color.w * 255)
        self.cache_texture.set_ram_image(ram_image)

        self.count_texture.clear_image()

        for np in np_list:
            material = np.find_all_materials()[0]
            material_idx = material_map[material.name]
            # print(np.name, material.name, material_idx)
            np.set_shader_input('material_index', material_idx)

    def bind(self, node_path):
        node_path.set_shader_input('material_cache', self.cache_texture)
