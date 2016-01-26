from kivy.graphics import Color, Rectangle, Canvas, ClearBuffers, ClearColor
from kivy.graphics.fbo import Fbo
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty, NumericProperty


class TransparentLayout(FloatLayout):
    texture = ObjectProperty(None, allownone=True)

    alpha = NumericProperty(1)

    def __init__(self, **kwargs):
        self.canvas = Canvas()

        with self.canvas:
            self.fbo = Fbo(
                size=self.size,
                with_depthbuffer=True,
            )
            self.fbo_color = Color(1, 1, 1, 1)
            self.viewport = Rectangle(
                pos=self.pos,
                size=self.size,
            )

        with self.fbo:
            ClearColor(0, 0, 0, 0)
            ClearBuffers()

        self.texture = self.fbo.texture

        super(TransparentLayout, self).__init__(**kwargs)

    def add_widget(self, *largs):
        canvas = self.canvas
        self.canvas = self.fbo
        ret = super(TransparentLayout, self).add_widget(*largs)
        self.canvas = canvas
        return ret

    def remove_widget(self, *largs):
        canvas = self.canvas
        self.canvas = self.fbo
        super(TransparentLayout, self).remove_widget(*largs)
        self.canvas = canvas

    def on_size(self, instance, value):
        self.fbo.size = value
        self.texture = self.fbo.texture
        self.viewport.size = value

    def on_texture(self, instance, value):
        self.viewport.texture = value

    def on_alpha(self, instance, value):
        self.fbo_color.rgba = (1, 1, 1, value)

    def on_pos(self, instance, value):
        self.viewport.pos = value
