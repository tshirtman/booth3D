'''
Panda View
==========
'''
from panda3d.core import (
    CollisionTraverser,
    CollisionRay,
    CollisionNode,
    CollisionHandlerQueue,
    Vec3,
    Point3,
    WindowProperties
)

from pandawrapper import ModelShowbase

from kivy.clock import Clock, ClockBase
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Callback, Fbo
from kivy.properties import (
    ListProperty,
    NumericProperty,
)
from kivy.graphics.opengl import glEnable, GL_DEPTH_TEST, GL_CULL_FACE
from math import cos, sin


class PandaView(Widget):
    cam_pos = ListProperty([0, 0, 0])
    cam_lookat = ListProperty([0, 0, 0])
    models = ListProperty([])   # Paths to models
    _models = ListProperty([])  # Actual models
    angles = ListProperty([])
    obj_pos = ListProperty([])

    def __init__(self, **kwargs):
        super(PandaView, self).__init__(**kwargs)
        self.setup_panda()

    def on_models(self, instance, values):
        for model in self._models:
            model.remove_node()
        return self.load_models(values)

    def load_models(self, filenames):
        models = []
        for model in filenames:
            models.append(self.msb.load_model(model))
        self._models = models
        return models

    def update_panda(self, *largs):
        self.canvas.ask_update()

    def setup_panda(self, *largs):
        self.msb = ModelShowbase()
        self.msb.camLens.setFov(52.0)
        self.msb.camLens.setNearFar(1.0, 10000.0)

        with self.canvas:
            self.fbo = Fbo(
                size=self.size
            )
            self.viewport = Rectangle(
                pos=self.pos,
                size=self.size,
            )
            Callback(
                self.draw_panda,
                reset_context=True
            )

        Clock.schedule_interval(self.update_panda, 1 / 60.)

    def draw_panda(self, instr):
        self.fbo.clear_buffer()
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        self.msb.taskMgr.step()

        self.msb.camera.setPos(Point3(*self.cam_pos))
        self.msb.camera.lookAt(Point3(*self.cam_lookat), Vec3(0, 0, 1))

    def toggle_show_collision_boxes(self):
        ''' Debug visualization: Toggle drawing of collision nodes.
            Off by default.
        '''
        # See http://www.panda3d.org/apiref.php?page=NodePath
        matches = self.msb.render.findAllMatches('**/+CollisionNode')
        if self._show_collision_boxes:
            matches.hide()
        else:
            matches.show()
        self._show_collision_boxes = not self._show_collision_boxes
        return self._show_collision_boxes

    def set_show_collision_boxes(self, value):
        if self._show_collision_boxes and value:
            return
        if not self._show_collision_boxes and not value:
            return
        self.toggle_show_collision_boxes()

    def to_panda_window(self, x, y):
        '''
        Convert Kivy window coordinates to panda window coordinates.
        The panda window coordinate system's origin is in the middle of the window,
        with the x-axis going positively to the right and the y axis pointing
        positively up, where coordinates in all directions are normalized to a
        float of maximum value 1. (i.e., top right corner is (1., 1.)).
        '''
        w, h = self.size
        w2 = w / 2.
        h2 = h / 2.
        x = (x - w2) / w2
        y = (y - h2) / h2
        return x, y

    def on_size(self, instance, value):
        self.fbo.size = value
        self.viewport.size = value

    def on_pos(self, instance, value):
        self.viewport.pos = value

    def on_angles(self, instance, values):
        for index, angle in enumerate(values):
            self._models[index].setHpr(angle * -360, 0, 0)

    def on_obj_pos(self, instance, values):
        for index, pos in enumerate(values):
            self._models[index].setPos(Vec3(*pos))
