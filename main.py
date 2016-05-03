# encoding: utf-8

from kivy.config import Config
Config.set('graphics', 'width', 1920)
Config.set('graphics', 'height', 1080)
Config.set('graphics', 'borderless', True)
Config.set('graphics', 'show_cursor', False)

from kivy.app import App
from kivy.lib import osc
from kivy.clock import Clock
from kivy.properties import (
    BooleanProperty,
    ListProperty,
    NumericProperty,
    ObjectProperty,
)
from kivy.animation import Animation
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.carousel import Carousel
from kivy.factory import Factory

from panda_wrapper import PandaView

import progressivelabel  # noqa

Factory.register(
    'ParticleSystem',
    module='kivy.garden.particlesystem.particlesystem'
)

Factory.register(
    'TransparentLayout',
    module='panda_wrapper'
)


SHOW_THRESHOLD = 50
HIDE_THRESHOLD = .02
Z = 6 * 10 ** -3
Z2 = 2 * 10 ** -3
TIMEOUT = 0


def standard_deviation(l):
    mean = sum(l) / len(l)
    mean_sq = sum(x ** 2 for x in l) / len(l)
    return (mean_sq - mean ** 2) ** .5


class Booth(App):
    data = ListProperty([])

    angle = NumericProperty(0)
    '''
    `angle` of the attached object, expressed in `to` (2 * `pi`).
    '''
    turn_count = NumericProperty(0)

    display_container = BooleanProperty(False)

    stds = ListProperty([])

    def __init__(self):
        super(Booth, self).__init__()
        self.titles_list = [
            u"PARFUMÉE",
            u"IDÉALE",
            u"SOYEUSE",
        ]


    def build(self):
        super(Booth, self).build()
        self.oscid = oscid = osc.listen(ipAddr='0.0.0.0', port=8000)
        osc.bind(oscid, self.update_data, '/update')
        Clock.schedule_interval(lambda *x: osc.readQueue(oscid), 0)
        self.root.ids.particle._parse_config('data/implosion.pex')
        self.root.ids.particle.start()

    def update_data(self, *args):
        # data: ax_d, ay_d, az_d, rz_d
        data = args[0][2:]
        self.data.append(data)
        # only keep 100 frames of history
        self.data = self.data[-20:]
        # check if any of the accelero detected a serious change over
        # the recent history
        self.stds = [standard_deviation([x[d] for x in self.data]) for d in range(3)]

        if min(self.stds) > Z:
            self.show_container()
        elif max(self.stds) < Z2:
            Clock.schedule_once(self.hide_container, TIMEOUT)

        if len(self.data) < 2:
            self.angle = data[-1]
            return

        if abs(self.data[-2][-1] - data[-1]) > .5:
            if data[-1] < 0:
                self.turn_count += 1
            else:
                self.turn_count -= 1

        angle = data[-1] + .5 + self.turn_count

        self.angle = -angle

    def show_container(self, *args):
        self.display_container = True

    def hide_container(self, *args):
        self.display_container = False

    def schedule_content(self):
        Clock.unschedule(self.show_content)
        Clock.schedule_once(self.show_content, 3)
        content = self.root.ids.container.ids.content
        self.hide_content()

    def show_content(self, *args):
        container = self.root.ids.container
        content = container.ids.content
        content.source = 'data/holo/' + [
            'rose',
            'miel',
            'abricot'
        ][container.ids.carousel.index] + '.png'
        Animation(opacity=1).start(content)
        self.show_glow()

    def hide_content(self, *args):
        container = self.root.ids.container
        content = container.ids.content
        Animation(opacity=0, d=.35).start(content)
        if content.opacity:
            a = (
                Animation(opacity=1, d=.25) +
                Animation(opacity=0, d=.25)
            )
            a.start(container.ids.glow)

    def show_glow(self):
        container = self.root.ids.container
        a = (
            Animation(opacity=1, d=.35) +
            Animation(opacity=0, d=.35)
        )
        a.start(container.ids.glow)

    def on_display_container(self, *args):
        cont = self.root.ids.container
        Clock.unschedule(self.hide_container)
        Animation.stop_all(cont)
        if self.display_container:
            cont.carousel_y_decal = -2
            cont.title_y_decal = -2
            Clock.schedule_once(self.display_title, 1)
            self.schedule_content()
        else:
            Clock.unschedule(self.display_title)
            Animation(title_y_decal=-2).start(cont)
            Clock.unschedule(self.show_content)
            self.hide_content()

    def display_title(self, *args):
        a = Animation(title_y_decal=0, d=.4, t='out_quad')
        a.bind(on_complete=self.display_carousel)
        a.start(self.root.ids.container)

    def display_carousel(self, animation, container, *args):
        a = Animation(carousel_y_decal=0, d=1, t='out_quad')
        a.start(container)


class Ingredients3DView(PandaView):
    start_animation = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(Ingredients3DView, self).__init__(**kwargs)
        self.animation = None

    def on_start_animation(self, instance, value):
        if self.animation:
            self.animation.cancel(self)
        if(not value):
            self.animation = animation = (
                Animation(cam_radius=50, t='out_quad') &
                Animation(opacity=0)
            )
            animation.bind(on_complete=self.stop_animation)
            animation.start(self)
            animation = Animation(z=-25)
            for node in self.nodes:
                animation.start(node)
        else:
            self.stop_animation()
            self.opacity = 1
            for i, node in enumerate(self.nodes):
                animation = (
                    Animation(d=i) +
                    Animation(z=0, t='out_elastic')
                )
                animation.start(node)

    def stop_animation(self, *args):
        for node in self.nodes:
            node.z = -5
        self.cam_radius = 7


if __name__ == '__main__':
    app = Booth()
    app.run()
