# encoding: utf-8

from kivy.config import Config
Config.set('graphics', 'width', 1920)
Config.set('graphics', 'height', 1080)
Config.set('graphics', 'borderless', True)
Config.set('graphics', 'show_cursor', False)

from kivy.app import App
from kivy.lib import osc
from kivy.clock import Clock
from kivy.properties import ListProperty
from kivy.properties import NumericProperty
from kivy.properties import BooleanProperty
from kivy.animation import Animation
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.carousel import Carousel
from kivy.factory import Factory

import progressivelabel  # noqa

Factory.register(
    'ParticleSystem',
    module='kivy.garden.particlesystem.particlesystem'
)

Factory.register(
    'TransparentLayout',
    module='panda_wrapper'
)

Factory.register(
    'PandaView',
    module='panda_wrapper'
)

SHOW_THRESHOLD = 50
HIDE_THRESHOLD = .02
Z = - .22
Z2 = - .25
TIMEOUT = 0


#class BoothView(View):
#    pass


class Booth(App):
    data = ListProperty([])

    angle = NumericProperty(0)
    '''
    `angle` of the attached object, expressed in `to` (2 * `pi`).
    '''
    turn_count = NumericProperty(0)

    display_container = BooleanProperty(False)

    def __init__(self):
        super(Booth, self).__init__()
        self.titles_list = [
            u"DU PLAISIR POUR VOTRE PEAU",
            u"RÉALISEZ VOTRE DIAGNOSTIC",
            u"UNE PEAU IDÉALE",
            u"NOTRE SAVOIR FAIRE"
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
        diff = 0
        for d in range(3):
            diff = max(diff,
                       max(x[d] for x in self.data) -
                       min(x[d] for x in self.data))

        diff = max(diff, data[2] - 1.0)

        if data[2] > Z:
        #if diff > SHOW_THRESHOLD or data[2] > Z:
            self.show_container()

        elif diff < HIDE_THRESHOLD and data[2] < Z2:
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

    def on_display_container(self, *args):
        cont = self.root.ids.container
        Clock.unschedule(self.hide_container)
        Animation.stop_all(cont)
        if self.display_container:
            cont.carousel_y_decal = -2
            cont.title_y_decal = -1
            cont.opacity = 1
            cont.pos_y = -.5
            a = Animation(pos_y=.5, d=2, t='out_elastic')
            Clock.schedule_once(self.display_title, 1)
            #a.bind(on_complete=self.display_title)
            a.start(cont)
        else:
            Animation(opacity=0, d=.5, t='out_quad').start(cont)

    def display_title(self, *args):
        a = Animation(title_y_decal=0, d=.4, t='out_quad')
        a.bind(on_complete=self.display_carousel)
        a.start(self.root.ids.container)

    def display_carousel(self, animation, container, *args):
        container.ids.carousel.flag = True
        a = Animation(carousel_y_decal=0, d=1, t='out_quad')
        a.bind(on_complete=container.ids.carousel.reset_flag)
        a.start(container)


class Container(RelativeLayout):
    pass


class TwizCarousel(Carousel):
    angle = NumericProperty(0)
    angle_offset = NumericProperty(0)
    angle_rotation_trigger = NumericProperty(0)
    __flag = BooleanProperty(False)

    def on_angle(self, *args):
        if self.angle > self.angle_offset + self.angle_rotation_trigger:
            self.angle_offset = self.angle
            if not self.__flag:
                self.__flag = True
                self.load_next()
        elif self.angle < self.angle_offset - self.angle_rotation_trigger:
            self.angle_offset = self.angle
            if not self.__flag:
                self.__flag = True
                self.load_previous()

    def reset_flag(self, *args):
        Clock.unschedule(self._reset_flag)
        Clock.schedule_once(self._reset_flag, .2)

    def _reset_flag(self, *args):
        self.__flag = False

if __name__ == '__main__':
    app = Booth()
    app.run()
