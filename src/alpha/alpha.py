import time
import ion

## Keyboard
class Keyboard:
    def __init__(self, *keys):
        self.__press = {k: [False, False] for k in keys}

    def update(self):
        for k, s in self.__press.items():
            s[0], s[1] = s[1], ion.keydown(k)

    def press(self, key: int) -> bool:
        return self.__press[key][1] and not self.__press[key][0]

    def release(self, key: int) -> bool:
        return not self.__press[key][1] and self.__press[key][0]

    # def watch(self, *keys):
    #     for key in keys:
    #         self.__press[key] = [False, False]

    # def unwatch(self, *keys):
    #     for key in keys:
    #         self.__press.pop(key)

## Event bus
class Event:
    def __init__(self, type: str | int, data: dict):
        self.type = type
        self.data = data
        self.cancelled = False

class EventBus:
    def __init__(self):
        self.__subs = []

    def subscribe(self, fn, *names, priority: int=0):
        self.__subs.append((priority, fn, names))
        self.__subs.sort(key=lambda s: s[0])
        return self

    def dispatch(self, name, **data):
        evt = Event(name, data)
        for _, fn, names in self.__subs:
            if names and name not in names:
                continue
            fn(evt)
        return evt

    # def clear(self):
    #     self.__subs.clear()

class Scene:
    def __init__(self):
        self._isDirty: bool = True

    def mark_dirty(self, evt) -> None:
        """ evt just so I can subscribe events """
        self._isDirty = True

    def mark_clean(self):
        self._isDirty = False

    def is_dirty(self) -> bool:
        return self._isDirty

    def on_start(self, app: "App") -> None:
        # To override
        ...

    def on_dispose(self, app: "App") -> None:
        # To override
        app.bus.clear()

    def update(self, app: "App") -> None:
        # To override
        ...

    def render(self) -> None:
        # To override
        self._isDirty = False

class SceneManager:
    def __init__(self):
        self.__stack = []

    def push(self, scene, ctx=None) -> Scene:
        self.__stack.append(scene)
        scene.on_start(ctx)
        return scene

    def pop(self, ctx=None) -> "SceneManager":
        self.__stack.pop().on_dispose(ctx)
        return self

    def change(self, scene, ctx=None) -> Scene:
        while len(self.__stack) > 0:
            self.pop(ctx)
        self.push(scene, ctx)
        return scene

    def current(self) -> Scene:
        if not self.__stack:
            raise RuntimeError("No scene in stack")
        return self.__stack[-1]

class App:
    def __init__(self):
        self.events       : EventBus     = EventBus()
        self.keyboard  : Keyboard     = Keyboard(ion.KEY_OK, ion.KEY_LEFT, ion.KEY_RIGHT, ion.KEY_UP, ion.KEY_DOWN)
        self.scenes    : SceneManager = SceneManager()
        self.is_running: bool         = True

        self.tickrate  : int   = 30
        self.frame_time: float = 1.0 / self.tickrate

    def run(self):
        while self.is_running:
            try:
                ts = time.monotonic()

                self.keyboard.update()
                self.scenes.current().update(self)
                self.scenes.current().render()

                elapsed = time.monotonic() - ts
                waiting = self.frame_time - elapsed
                if waiting > 0:
                    time.sleep(waiting)

            except RuntimeError:
                break

    def set_tickrate(self, x : int):
        self.tickrate = x

    def stop(self):
        self.is_running = False