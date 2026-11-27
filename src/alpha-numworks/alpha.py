import os
os.environ["KANDINSKY_OS_MODE"] = '2' # set the os mode to Omega
import ion
import kandinsky
import time
import tracemalloc

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
        self.name: str = type(self).__name__

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

class Debug:
    def __init__(self):
        self._scene_label_width = 0
        tracemalloc.start()
        self._tracemalloc = tracemalloc

    def show_info(self, app):
        if isinstance(app, App):
            fps = str(round(1 / app.frame_duration))
            kandinsky.draw_string(f"FPS: {fps}/{app.tickrate}", 0, 0, (0, 0, 0), (248, 252, 248), True)

            scene_label = f"Scene: {app.scenes.current().name}"
            kandinsky.draw_string(scene_label, 0, 12, (0, 0, 0), (248, 252, 248), True)

            gc_label = "GC: n/d"
            if self._tracemalloc is not None:
                used, total = self._tracemalloc.get_traced_memory()
                if total > 0:
                    gc_label = f"GC: {used}/{total} ({used * 100 // total}%)"
            kandinsky.draw_string(gc_label, 0, 24, (0, 0, 0), (248, 252, 248), True)

            self._scene_label_width = len(scene_label)

class App:
    def __init__(self, debug = False):
        self.events       : EventBus  = EventBus()
        self.keyboard  : Keyboard     = Keyboard(ion.KEY_OK, ion.KEY_LEFT, ion.KEY_RIGHT, ion.KEY_UP, ion.KEY_DOWN)
        self.scenes    : SceneManager = SceneManager()
        self.is_running: bool         = True
        self.debug: bool              = debug

        self.tickrate  : int   = 30
        self.frame_time: float = 1.0 / self.tickrate
        self.frame_duration = None

    def run(self):
        debugger = Debug()
        previous_frame_start = None
        while self.is_running:
            try:
                ts = time.monotonic()

                self.keyboard.update()
                self.scenes.current().update(self)
                scene = self.scenes.current()
                scene.render()

                if self.debug:
                    self.frame_duration = 1 if previous_frame_start is None else ts - previous_frame_start
                    debugger.show_info(self)
                previous_frame_start = ts

                elapsed = time.monotonic() - ts
                waiting = self.frame_time - elapsed
                if waiting > 0:
                    time.sleep(waiting)

            except RuntimeError:
                break

    def set_tickrate(self, x : int):
        if x <= 0:
            raise ValueError("Tick rate must be positive")
        self.frame_time = 1.0 / x
        self.tickrate = x

    def stop(self):
        self.is_running = False
