#pylint: disable=missing-docstring
import os
import sys

from direct.showbase.ShowBase import ShowBase #pylint: disable=import-error
import panda3d.core as p3d
import blenderpanda

from material_cache import MaterialCache
from mesh_cache import MeshCache
from draw_manager import DrawManager

p3d.load_prc_file_data(
    '',
    'framebuffer-srgb true\n'
    'win-size 1280 720\n'
    'show-frame-rate-meter true\n'
    'frame-rate-meter-milliseconds true\n'
    'textures-power-2 false\n'
    'gl-immutable-texture-storage true\n'
    # 'show-buffers #t\n'
    'gl-debug #t\n'
    'sync-video false\n'
)

#pylint: disable=missing-docstring
class GameApp(ShowBase): #pylint: disable=too-few-public-methods
    def __init__(self):
        ShowBase.__init__(self)
        blenderpanda.init(self)
        self.accept('escape', sys.exit)

        self.setup_fafnir()

        # Scene Setup
        scene = self.loader.load_model('happy.bam')
        self.happy = scene.find('happy')
        if hasattr(self, 'fafnir_np'):
            scene.reparent_to(self.fafnir_np)
            self.node_paths = self.fafnir_np.find_all_matches('**/+GeomNode')
            self.material_list = self.fafnir_np.find_all_materials()
            self.mesh_cache.update(self.node_paths)
            self.mesh_cache.bind(self.fafnir_np)
            self.material_cache.update(self.material_list, self.node_paths)
            self.mesh_cache.bind(self.fafnir_np)
            # win_width = self.win.get_x_size()
            # win_height = self.win.get_y_size()
            # self.draw_manager.update(len(self.material_list), win_width, win_height)
        else:
            scene.reparent_to(self.render)
        taskMgr.add(self.rotate_happy_task, 'Why is the room spinning?')

    def setup_fafnir(self):
        self.fafnir_np = p3d.NodePath(p3d.PandaNode("Fafnir"))
        global_shader = p3d.Shader.load(
            p3d.Shader.SL_GLSL,
            vertex="shaders/build_mesh_cache.vs",
            geometry="shaders/build_mesh_cache.gs",
            fragment="shaders/generate_primary_intersections.fs",
        )
        self.fafnir_np.set_shader(global_shader)
        self.mesh_cache = MeshCache(1, 1)
        self.material_cache = MaterialCache()
        self.draw_manager = DrawManager(self.fafnir_np)

        win_width = self.win.get_x_size()
        win_height = self.win.get_y_size()
        rtt_fb_prop = p3d.FrameBufferProperties()
        rtt_fb_prop.set_rgba_bits(32, 32, 32, 32)
        rtt_fb_prop.set_float_color(True)
        rtt_fb_prop.set_depth_bits(32)
        rtt_win_prop = p3d.WindowProperties().size(win_width, win_height)
        rtt_buffer = base.graphics_engine.make_output(
            base.pipe,
            'Fafnir RTT Buffer',
            -100,
            rtt_fb_prop,
            rtt_win_prop,
            p3d.GraphicsPipe.BF_refuse_window,
            base.win.get_gsg(),
            base.win
        )
        intersection_texture = p3d.Texture()
        rtt_buffer.add_render_texture(
            intersection_texture,
            p3d.GraphicsOutput.RTM_bind_or_copy,
            p3d.GraphicsOutput.RTP_color
        )
        rtt_cam = base.make_camera(rtt_buffer)
        rtt_cam.reparent_to(self.fafnir_np)

        vdata = p3d.GeomVertexData(
            'empty',
            p3d.GeomVertexFormat.get_empty(),
            p3d.GeomEnums.UH_static
        )
        resolve_shader = p3d.Shader.load(
            p3d.Shader.SL_GLSL,
            vertex='shaders/resolve_intersections.vs',
            fragment='shaders/resolve_intersections.fs'
        )

        self.int_texture = intersection_texture
        self.draw_manager.set_inputs(self.int_texture, self.material_cache.count_texture)

        self.temp_nps = []
        def cb_update_draw_calls(cbdata):
            for np in self.temp_nps:
                np.remove_node()
            self.temp_nps = []

            tex = self.draw_manager._indirect_buffer
            gsg = self.win.get_gsg()
            if self.graphics_engine.extract_texture_data(tex, gsg):
                tex_view = memoryview(tex.get_ram_image()).cast('i')
                for call_idx in range(tex.get_x_size()):
                    i = call_idx*4
                    primcount = tex_view[i+1]
                    first = tex_view[i+2]

                    prims = p3d.GeomPoints(p3d.GeomEnums.UH_dynamic)
                    prims.add_next_vertices(primcount)
                    geom = p3d.Geom(vdata)
                    geom.add_primitive(prims)
                    geom.set_bounds(p3d.OmniBoundingVolume())
                    node = p3d.GeomNode('Draw Call {}'.format(call_idx))
                    node.add_geom(geom)
                    path = p3d.NodePath(node)
                    path.set_bin('fixed', 50)
                    path.set_depth_test(False)
                    path.set_depth_write(False)
                    path.set_shader(resolve_shader)
                    path.set_shader_input('first', first)
                    window_size = p3d.LVector2i(win_width, win_height)
                    path.set_shader_input('window_size', window_size)
                    path.set_shader_input('vertex_cache', self.mesh_cache.vert_texture)
                    path.set_shader_input('index_cache', self.mesh_cache.index_texture)
                    path.set_shader_input('intersections', self.int_texture)
                    self.material_cache.bind(path)
                    path.reparent_to(self.render)
                    self.temp_nps.append(path)
            cbdata.upcall()

        cbnode = p3d.CallbackNode('UpdateDrawCalls')
        cbnode.set_draw_callback(p3d.PythonCallbackObject(cb_update_draw_calls))
        cb_np = self.render.attach_new_node(cbnode)
        cb_np.set_bin('fixed', 45)
        # taskMgr.add(task_update_draw_calls, 'Update Draw Calls', sort=55)

        def task_fafnir(task):
            # node_paths = self.fafnir_np.find_all_matches('**/+GeomNode')
            # self.material_list = self.fafnir_np.find_all_materials()
            # self.mesh_cache.update(self.node_paths)
            # self.mesh_cache.bind(self.fafnir_np)
            self.material_cache.update(self.material_list, self.node_paths)
            win_width = self.win.get_x_size()
            win_height = self.win.get_y_size()
            self.draw_manager.update(len(self.material_list), win_width, win_height)
            return task.cont
        taskMgr.add(task_fafnir, 'Gather mesh data')

        def read_texture():
            tex = self.draw_manager._indirect_buffer
            gsg = self.win.get_gsg()
            if self.graphics_engine.extract_texture_data(tex, self.win.get_gsg()):
                view = memoryview(tex.get_ram_image()).cast('i')
                for i in range(16):
                    if i % 4 == 0:
                        print()
                    print(view[i])
                # success = tex.write(p3d.Filename('vertex_cache.png'))
                # print('Texture write: ', success)
            else:
                print('texture has no RAM image')
        self.accept('f1', read_texture)

    def rotate_happy_task(self, task):
        hpr = self.happy.get_hpr()
        hpr.x += 50 * globalClock.get_dt()
        self.happy.set_hpr(hpr)
        return task.cont


APP = GameApp()
APP.run()
