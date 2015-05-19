from kivy.app import App
from kivy.garden.ddd import View
from kivy.lib import osc
from kivy.clock import Clock
from kivy.properties import ListProperty
from kivy.properties import NumericProperty
from kivy.properties import BooleanProperty
from kivy.animation import Animation
from kivy.uix.relativelayout import RelativeLayout
from kivy.factory import Factory

import ddd  # noqa

Factory.register('ParticleSystem',
                 module='kivy.garden.particlesystem.particlesystem')

SHOW_THRESHOLD = .2
HIDE_THRESHOLD = .1
TIMEOUT = 1


class BoothView(View):
    pass


class Booth(App):
    data = ListProperty([])

    angle = NumericProperty(0)
    '''
    `angle` of the attached object, expressed in `to` (2 * `pi`).
    '''

    display_container = BooleanProperty(False)

    def build(self):
        super(Booth, self).build()
        self.oscid = oscid = osc.listen(ipAddr='0.0.0.0', port=8000)
        osc.bind(oscid, self.update_data, '/update')
        self.turn_count = 0
        Clock.schedule_interval(lambda *x: osc.readQueue(oscid), 0)

    def update_data(self, *args):
        # data: ax_d, ay_d, az_d, rz_d
        data = args[0][2:]
        self.data.append(data)
        # only keep 100 frames of history
        self.data = self.data[-100:]
        # check if any of the accelero detected a serious change over
        # the recent history
        diff = 0
        for d in range(3):
            diff = max(diff,
                       max(x[d] for x in self.data) -
                       min(x[d] for x in self.data))

        if diff > SHOW_THRESHOLD:
            self.show_container()

        elif diff < HIDE_THRESHOLD:
            Clock.schedule_once(self.hide_container, TIMEOUT)

        if len(self.data) < 2:
            self.angle = data[-1]
            return

        if abs(self.data[-2][-1] - data[-1]) > .5:
            if data[-1] < 0:
                self.turn_count += 1
            else:
                self.turn_count -= 1

        angle = data[-1] + self.turn_count

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
            Animation(pos_y=.5, t='out_elastic').start(cont)
        else:
            Animation(pos_y=-.5, t='out_quad').start(cont)


class Container(RelativeLayout):
    pass


if __name__ == '__main__':
    app = Booth()
    app.run()
