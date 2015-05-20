from kivy.uix.label import Label
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.clock import Clock


class ProgressiveLabel(Label):
    target_text = StringProperty('')
    interval = NumericProperty(0.07)
    repeat = BooleanProperty(False)
    repeat_delay = NumericProperty(0)

    def on_target_text(self, *args):
        Clock.unschedule(self.update_text)
        self.text = ' '
        if self.target_text:
            Clock.schedule_interval(self.update_text, self.interval)

    def update_text(self, *args):
        if self.text == ' ':
            self.text = ''
        self.text += self.target_text[len(self.text)]
        if self.text == self.target_text:
            if self.repeat:
                Clock.schedule_once(self.reset_text, self.repeat_delay)
            return False

    def reset_text(self, *args):
        self.text = self.target_text[0]
        Clock.schedule_interval(self.update_text, self.interval)
