from flexx import app, ui, react

class Example(ui.Widget):

  def init(self):
    self.count = 0
    with ui.HBox():
      self.button = ui.Button(text='Click me', flex=0)
      self.label = ui.Label(flex=1)

  @react.connect('button.mouse_down')
  def _handle_click(self, down):
    if down:
      self.count += 1
      self.label.text('clicked %i times' % self.count)

main = app.launch(Example)
app.run()
