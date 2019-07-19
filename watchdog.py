from time import sleep
import threading

class Watchdog:
    def __init__(self, precision, timeout, callback):
        self.precision = precision
        self.timeout = timeout
        self.callback = callback

        self.elapsed = 0

        self.run = True

        self.watchdog_thread = threading.Thread(target=self._mainloop, daemon=True)
        self.watchdog_thread.start()
    
    def _mainloop(self):
        while self.run:
            sleep(self.precision/1000)
            self.elapsed += self.precision
            if(self.elapsed >= self.timeout):
                self.callback()
    
    def reset(self):
        self.elapsed = 0

        