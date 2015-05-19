from kivy.app import App
from kivy.garden.ddd import View
from kivy.lib import osc
from kivy.clock import Clock
from kivy.properties import ListProperty
from kivy.properties import NumericProperty
from kivy.properties import BooleanProperty
from kivy.animation import Animation
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.carousel import Carousel
from kivy.factory import Factory

import ddd  # noqa

Factory.register('ParticleSystem',
                 module='kivy.garden.particlesystem.particlesystem')

SHOW_THRESHOLD = .2
HIDE_THRESHOLD = .02
Z = .25
TIMEOUT = 0


class BoothView(View):
    pass


class Booth(App):
    data = ListProperty([])

    angle = NumericProperty(0)
    '''
    `angle` of the attached object, expressed in `to` (2 * `pi`).
    '''
    turn_count = NumericProperty(0)

    display_container = BooleanProperty(False)

    def build(self):
        super(Booth, self).build()
        self.oscid = oscid = osc.listen(ipAddr='0.0.0.0', port=8000)
        osc.bind(oscid, self.update_data, '/update')
        Clock.schedule_interval(lambda *x: osc.readQueue(oscid), 0)
        self.root.ids.particle.start()
        self.root.ids.particle.config = 'data/implosion.pex'

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

        if diff > SHOW_THRESHOLD or abs(data[2] - Z) > SHOW_THRESHOLD:
            self.show_container()

        elif diff < HIDE_THRESHOLD and abs(data[2] - Z) < HIDE_THRESHOLD / 10:
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

        self.angle = angle

    def show_container(self, *args):
        self.display_container = True

    def hide_container(self, *args):
        self.display_container = False

    def on_display_container(self, *args):
        cont = self.root.ids.container
        Clock.unschedule(self.hide_container)
        Animation.stop_all(cont)
        if self.display_container:
            a = Animation(pos_y=.5, d=2, t='out_elastic')
            a.bind(on_complete=self.display_carousel)
            a.start(cont)
        else:
            Animation.stop_all(cont.ids.carousel)
            Animation(opacity=0, d=.2, t='out_quad').start(cont.ids.carousel)
            Animation(pos_y=-.5, t='out_quad').start(cont)

    def display_carousel(self, animation, container, *args):
        Animation.stop_all(container.ids.carousel)
        Animation(opacity=1, d=.5, t='out_quad').start(container.ids.carousel)


class Container(RelativeLayout):
    pass


class TwizCarousel(Carousel):
    angle = NumericProperty(0)
    angle_offset = NumericProperty(0)
    angle_rotation_trigger = NumericProperty(0)

    def on_angle(self, *args):
        if self.angle > self.angle_offset + self.angle_rotation_trigger:
            self.angle_offset = self.angle
            self.load_next()
        elif self.angle < self.angle_offset - self.angle_rotation_trigger:
            self.angle_offset = self.angle
            self.load_previous()

if __name__ == '__main__':
    app = Booth()
    app.run()
