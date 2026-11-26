import src.alpha.alpha as alpha
from kandinsky import fill_rect


class MainScene(alpha.Scene):
    def update(self, app):
        pass

    def render(self):
        fill_rect(100, 100, 50, 50, (255, 0, 0))


app = alpha.App(True)
app.scenes.push(MainScene())
app.run()
