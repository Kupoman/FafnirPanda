import panda3d.core as p3d


class DrawManager:
    def __init__(self, fafnir_np):
        self._count_np = p3d.NodePath(p3d.ComputeNode('FDM_comp_count'))
        self._count_np.reparent_to(fafnir_np)
        count_shader = p3d.Shader.load_compute(
            p3d.Shader.SL_GLSL,
            'shaders/count_materials.cs'
        )
        self._count_np.set_shader(count_shader)
        self._count_np.set_bin('fixed', 40)

        self._call_np = p3d.NodePath(p3d.ComputeNode('FDM_comp_call'))
        self._call_np.reparent_to(fafnir_np)
        count_shader = p3d.Shader.load_compute(
            p3d.Shader.SL_GLSL,
            'shaders/create_draw_calls.cs'
        )
        self._call_np.set_shader(count_shader)
        self._call_np.set_bin('fixed', 41)

        self._sort_np = p3d.NodePath(p3d.ComputeNode('FDM_comp_sort'))
        self._sort_np.reparent_to(fafnir_np)
        count_shader = p3d.Shader.load_compute(
            p3d.Shader.SL_GLSL,
            'shaders/sort_intersections.cs'
        )
        self._sort_np.set_shader(count_shader)
        self._sort_np.set_bin('fixed', 42)

        self._indirect_buffer = p3d.Texture()
        self.draw_count = 0

        self._sorted_buffer = p3d.Texture()
        self.ray_count = 0

        self.ensure_sizes(1, 1)

    def ensure_sizes(self, draw_count, ray_count):
        if draw_count > self.draw_count:
            self.draw_count = draw_count
            self._indirect_buffer.setup_buffer_texture(
                draw_count,
                p3d.Texture.T_unsigned_int,
                p3d.Texture.F_rgba32,
                p3d.GeomEnums.UH_dynamic
            )
            # self._indirect_buffer.set_clear_color(p3d.LColor(1.0, 0.0, 0.0, 0.0))
            # self._indirect_buffer.clear_image()

        if ray_count > self.ray_count:
            self.ray_count = ray_count
            self._sorted_buffer.setup_buffer_texture(
                ray_count,
                p3d.Texture.T_unsigned_int,
                p3d.Texture.F_r32i,
                p3d.GeomEnums.UH_dynamic
            )

    def update(self, draw_count, ray_count_x, ray_count_y):
        self.ensure_sizes(draw_count, ray_count_x * ray_count_y)

        node = self._count_np.node()
        node.clear_dispatches()
        node.add_dispatch(ray_count_x, ray_count_y, 1)

        node = self._call_np.node()
        node.clear_dispatches()
        node.add_dispatch(draw_count, 1, 1)

        node = self._sort_np.node()
        node.clear_dispatches()
        node.add_dispatch(ray_count_x, ray_count_y, 1)

    def set_inputs(self, intersections, counts):
        self._count_np.set_shader_input('intersections', intersections)
        self._count_np.set_shader_input('material_counts', counts, True, True, -1, 0)

        self._call_np.set_shader_input('material_counts', counts)
        self._call_np.set_shader_input('draw_calls', self._indirect_buffer, False, True, -1, 0)

        self._sort_np.set_shader_input('intersections', intersections)
        self._sort_np.set_shader_input('draw_calls', self._indirect_buffer)
        self._sort_np.set_shader_input('material_counts', counts, True, True, -1, 0)
        self._sort_np.set_shader_input('sorted_indexes', self._sorted_buffer, False, True, -1, 0)
