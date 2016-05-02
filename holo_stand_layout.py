from textwrap import dedent

from kivy.graphics import Color, Rectangle, Canvas, ClearBuffers, ClearColor, Rotate, Triangle
from kivy.graphics.fbo import Fbo
from kivy.graphics.stencil_instructions import StencilPush, StencilUse, StencilUnUse, StencilPop
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty, NumericProperty
from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder


class HoloStandLayout(FloatLayout):
    texture = ObjectProperty(None, allownone=True)

    alpha = NumericProperty(1)

    def __init__(self, **kwargs):
        self.canvas = Canvas()

        window_width = Window.width
        window_height = Window.height

        aspect = window_width / float(window_height)

        center_x = window_width / 2.
        center_y = window_height / 2.

        element_size = window_width

        with self.canvas:
            self.fbo = Fbo(size=self.size, with_depthbuffer=True)
            self.fbo_color = Color(1, 1, 1, 1)
            self.fbo_rects = (
                StencilPush(),
                Triangle(
                    points=(
                        0, 0,
                        center_x * 1.5, window_height,
                        0, window_height,
                    )
                ),
                StencilUse(),

                Rotate(
                    angle=-90,
                    axis=(0, 0, 1),
                    origin=(center_x, window_height * 2 / 3.)
                ),

                Rectangle(
                    pos=(
                        center_x - element_size / 2.,
                        -5
                    ),
                    size=(
                        element_size,
                        element_size / aspect
                    ),
                    texture=self.texture
                ),

                Rotate(
                    angle=90,
                    axis=(0, 0, 1),
                    origin=(center_x, window_height * 2 / 3.)
                ),

                StencilUnUse(),
                Triangle(
                    points=(
                        0, 0,
                        center_x * 1.5, window_height,
                        0, window_height,
                    )
                ),
                StencilPop(),

                StencilPush(),
                Triangle(
                    points=(
                        window_width, 0,
                        center_x * .5, window_height,
                        window_width, window_height,
                    )
                ),
                StencilUse(),

                Rotate(
                    angle=90,
                    axis=(0, 0, 1),
                    origin=(center_x, window_height * 2 / 3.)
                ),

                Rectangle(
                    pos=(
                        center_x - element_size / 2.,
                        -5
                    ),
                    size=(
                        element_size,
                        element_size / aspect
                    ),
                    texture=self.texture
                ),


            )

            Rotate(
                angle=-90,
                axis=(0, 0, 1),
                origin=(center_x, window_height * 2 / 3.)
            )

            StencilUnUse()
            Triangle(
                points=(
                    window_width, 0,
                    center_x * .5, window_height,
                    window_width, window_height,
                )
            )
            StencilPop()

            StencilPush()
            Triangle(
                points=(
                    0, 0,
                    window_width, 0,
                    center_x, window_height * 2 / 3.,
                )
            )
            StencilUse()

            if self.texture:
                self.texture.flip_horizontal()
            self.mirrored_rect = Rectangle(
                pos=(
                    center_x - element_size / 2.,
                    0
                ),
                size=(
                    element_size,
                    element_size / aspect
                ),
                texture=self.texture
            )

            StencilUnUse()
            Triangle(
                points=(
                    0, 0,
                    window_width, 0,
                    center_x, window_height * 2 / 3.,
                )
            )
            StencilPop()

        with self.fbo:
            ClearColor(0, 0, 0, 0)
            ClearBuffers()

        self.texture = self.fbo.texture
        super(HoloStandLayout, self).__init__(**kwargs)

    def add_widget(self, *largs):
        canvas = self.canvas
        self.canvas = self.fbo
        ret = super(HoloStandLayout, self).add_widget(*largs)
        self.canvas = canvas
        return ret

    def remove_widget(self, *largs):
        canvas = self.canvas
        self.canvas = self.fbo
        super(HoloStandLayout, self).remove_widget(*largs)
        self.canvas = canvas

    def on_size(self, instance, value):
        self.fbo.size = value
        self.texture = self.fbo.texture

    def on_texture(self, instance, value):
        self.mirrored_rect.texture = value
        for rect in self.fbo_rects:
            if hasattr(rect, 'texture'):
                rect.texture = value

    def on_alpha(self, instance, value):
        self.fbo_color.rgba = (1, 1, 1, value)

if __name__ == "__main__":
    class ScreenLayerApp(App):
        def build(self):
            f = HoloStandLayout()
            f.add_widget(Builder.load_string(dedent('''
                BoxLayout:
                    orientation: 'vertical'

                    Button:
                        text: 'Hello,'
                    Button:
                        text: 'World!'
            ''')))

            return f

    ScreenLayerApp().run()
