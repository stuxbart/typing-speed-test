import time


class Clock:
    def __init__(self, init=False):
        self._system_time = time.perf_counter
        self._system_time_last = self._system_time()
        self._time = 0.0
        self._running = False
        self._initialized = False
        self._widget = None
        self._speed = 1.0
        if init:
            self.start()

    @property
    def time(self):
        return self._time

    def start(self):
        self._running = True
        if not self._initialized:
            self._system_time_last = self._system_time()
            self._initialized = True

    def stop(self):
        self._running = False

    def change_time(self, dt):
        self._time += dt

    def set_time(self, t):
        self._time = t

    def reset_time(self):
        self.set_time(0.0)

    def bind_widget(self, w):
        self._widget = w

    def update_widget_time(self):
        if self._widget:
            self._widget.setText(f"T: {self.time:.2f}s")

    def tick(self):
        if self._running:
            dt = self._system_time() - self._system_time_last
            self._time += dt * self._speed
        self._system_time_last = self._system_time()

    def set_speed(self, s):
        self._speed = s
