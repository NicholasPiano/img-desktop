from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse
from kivy.core.window import Window
from kivy.clock import Clock

class PaintWidget(Widget):
  def on_touch_down(self, touch):
    with self.canvas:
      Color(1, 1, 0)
      d = 30.
      Ellipse(pos=(touch.x - d / 2, touch.y - d / 2), size=(d, d))

class PaintApp(App):
  def build(self):
    return PaintWidget()

  def on_motion(self, etype, motionevent):
    # will receive all motion events.
    print('hello')

  Window.bind(on_mouse_move=on_motion)
