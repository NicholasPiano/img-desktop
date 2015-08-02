from kivy.app import App
from kivy.uix.widget import Widget

class PaintWidget(Widget):
  def on_touch_down(self, touch):
    print(touch)

class PaintApp(App):
  def build(self):
    return PaintWidget()
