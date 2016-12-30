"""
A simple file that writes to a texture buffer with a compute shader and then
attempts to extract the texture data. This should print out the numbers 0-9.
Preferably without any OpenGL errors.
"""


import sys

from direct.showbase.ShowBase import ShowBase
import panda3d.core as p3d


p3d.load_prc_file_data('', 'gl-debug #t\n')


SHADER_SRC = """
#version 430
layout(size1x32) uniform restrict writeonly iimage1D test_buffer;
layout (local_size_x = 1, local_size_y = 1, local_size_z = 1) in;
void main()
{
    int i = int(gl_GlobalInvocationID.x);
    imageStore(test_buffer, i, ivec4(i, 0, 0, 0));
}
"""


class GameApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.accept('escape', sys.exit)

        texture = p3d.Texture()
        texture.setup_buffer_texture(
            10,
            p3d.Texture.T_unsigned_int,
            p3d.Texture.F_rgba32,
            p3d.GeomEnums.UH_dynamic
        )

        gsg = self.win.get_gsg()
        pobs = gsg.get_prepared_objects()
        tex_ctx = texture.prepare_now(0, pobs, gsg)

        compute_node = p3d.ComputeNode('compute_node')
        compute_node.add_dispatch(10, 1, 1)
        compute_np = p3d.NodePath(compute_node)
        compute_np.reparent_to(self.render)
        compute_shader = p3d.Shader.make_compute(p3d.Shader.SL_GLSL, SHADER_SRC)
        compute_np.set_shader(compute_shader)
        compute_np.set_shader_input('test_buffer', texture, False, True, -1, 0)

        def extract_texture(task):
            self.graphics_engine.extract_texture_data(texture, self.win.get_gsg())
            view = memoryview(texture.get_ram_image()).cast('i')
            for i in range(10):
                print(view[i], end=' ')
            print()
            return task.cont
        taskMgr.add(extract_texture, 'extract_texture', sort=55)


GameApp().run()
