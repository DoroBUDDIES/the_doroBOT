import threading
import time
import RPi.GPIO as GPIO
from PIL import Image, ImageSequence
from luma.core.interface.serial import spi
from luma.lcd.device import ili9341

class Display:
    def __init__(self):
        # TFT Display Setup
        self.serial = spi(device=0, port=0, gpio_DC=24, gpio_RST=25, bus_speed_hz=52000000)
        self.device = ili9341(self.serial, width=320, height=240, rotate=0)

        self.frames = []
        self.frame_count = 0

        self._running = False
        self._thread = None

    def load_gif(self, gif_path):
        """Load frames from GIF file"""
        self.frames.clear()

        gif = Image.open(gif_path)

        for frame in ImageSequence.Iterator(gif):
            frame_rgb = frame.convert("RGB").resize(
                (self.device.width, self.device.height)
            )
            self.frames.append(frame_rgb)

        self.frame_count = len(self.frames)
        print(f"Loaded {self.frame_count} frames from {gif_path}")

    def _playback_loop(self):
        frame_index = 0
        while self._running and self.frame_count > 0:
            self.device.display(self.frames[frame_index])
            frame_index = (frame_index + 1) % self.frame_count
            # time.sleep(0.03)

    def start(self):
        """Start playback in background thread"""
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self._playback_loop)
            self._thread.daemon = True
            self._thread.start()

    def stop(self):
        """Stop playback"""
        self._running = False
        if self._thread:
            self._thread.join()

if __name__ == '__main__':
    screen = Display()

    img = Image.new("RGB", (320, 240), (255, 0, 0))
    screen.device.display(img)
    time.sleep(2)

    screen.load_gif("../assets/herry.gif")
    
    screen._running = True
    screen._playback_loop()
