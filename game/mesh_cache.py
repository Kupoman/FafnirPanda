import panda3d.core as p3d


class MeshCache:
    def __init__(self, vert_count=2**20, tri_count=2**20):
        self.max_vert_count = 0
        self.max_tri_count = 0

        self.vert_texture = p3d.Texture()
        self.index_texture = p3d.Texture()

        self.ensure_sizes(vert_count, tri_count)

    def ensure_sizes(self, vert_count, tri_count):
        size_updated = False
        if vert_count > self.max_vert_count:
            self.max_vert_count = vert_count
            self.resize_vert_texture()
            size_updated = True
        if tri_count > self.max_tri_count:
            self.max_tri_count = tri_count
            self.resize_index_texture()
            size_updated = True

        if size_updated:
            # print("MeshCache V: {} I: {}".format(self.max_vert_count, self.max_tri_count))
            mem_size = self.get_memory_size()
            if mem_size > 2**20:
                print("MeshCache size: {:.2}MB".format(mem_size/2**20))
            else:
                print("MeshCache size: {}KB".format(mem_size/2**10))

    def resize_vert_texture(self):
        self.vert_texture.setup_buffer_texture(
            self.max_vert_count*2,
            p3d.Texture.T_float,
            p3d.Texture.F_rgba32,
            p3d.GeomEnums.UH_dynamic
        )
        # self.vert_texture.make_ram_image()

    def resize_index_texture(self):
        self.index_texture.setup_buffer_texture(
            self.max_tri_count*3,
            p3d.Texture.T_int,
            p3d.Texture.F_r32i,
            p3d.GeomEnums.UH_dynamic
        )
        # self.index_texture.make_ram_image()

    def update(self, np_list):
        vert_size = 0
        tri_size = 0
        for np in np_list:
            np.set_shader_input('vert_offset', vert_size)
            np.set_shader_input('index_offset', tri_size)
            for node in np.get_nodes():
                if node.name == 'FafnirRenderNode':
                    continue
                if type(node) == p3d.GeomNode:
                    for geom in node.get_geoms():
                        for prim in geom.get_primitives():
                            vert_size += prim.get_num_vertices()
                            tri_size += prim.get_num_faces()
        self.ensure_sizes(vert_size, tri_size)

    def bind(self, node_path):
        node_path.set_shader_input('vertex_cache', self.vert_texture, False, True, -1, 0)
        node_path.set_shader_input('index_cache', self.index_texture, False, True, -1, 0)

    def get_memory_size(self):
        return self.max_vert_count * 32 + self.max_tri_count * 12
