import time
from datetime import datetime
import os

import cv2
import numpy as np
from PIL import Image, ImageSequence, ImageFont, ImageDraw

from picamera2 import Picamera2

from luma.core.interface.serial import spi
from luma.lcd.device import ili9341

if False:  # For type hints only; not actually imported at runtime
    pass
    # class LCD:
    #     def __init__(self, width=320, height=240, rotate=0):
    #         # Adjust pins if yours differ
    #         self.serial = spi(
    #             device=0,
    #             port=0,
    #             gpio_DC=24,
    #             gpio_RST=25,
    #             bus_speed_hz=52000000
    #         )
    #         self.device = ili9341(self.serial, width=width, height=height, rotate=rotate)
    #         self.width = width
    #         self.height = height

    #         # For gif purposes
    #         self.frames = []
    #         self.frame_count = 0

    #         self._running = False

    #     def load_gif(self, gif_path):
    #         """Load frames from GIF file"""
    #         self.frames.clear()

    #         gif = Image.open(gif_path)

    #         for frame in ImageSequence.Iterator(gif):
    #             frame_rgb = frame.convert("RGB").resize(
    #                 (self.device.width, self.device.height)
    #             )
    #             self.frames.append(frame_rgb)

    #         self.frame_count = len(self.frames)
    #         print(f"Loaded {self.frame_count} frames from {gif_path}")

    #     def _playback_loop(self):
    #         frame_index = 0
    #         while self._running and self.frame_count > 0:
    #             self.device.display(self.frames[frame_index])
    #             frame_index = (frame_index + 1) % self.frame_count
    
    #     def show_bgra_frame(self, frame_bgra):
    #         """
    #         frame_bgra: numpy array (H, W, 4) from Picamera2 XRGB8888 capture
    #         Converts to RGB PIL and pushes to LCD.
    #         """
    #         # Try BGRA -> RGB first (most common with Picamera2 XRGB8888)
    #         rgb = cv2.cvtColor(frame_bgra, cv2.COLOR_BGRA2RGB)
    #         img = Image.fromarray(rgb)  # already correct size
    #         self.device.display(img)


    # class FaceDetectorLCD:
    #     def __init__(self, width=320, height=240):
    #         self.width = width
    #         self.height = height

    #         # --- camera ---
    #         self.camera = Picamera2()
    #         self.camera.configure(
    #             self.camera.create_preview_configuration(
    #                 main={"format": "XRGB8888", "size": (self.width, self.height)}
    #             )
    #         )
    #         self.camera.start()

    #         # --- lcd ---
    #         self.lcd = LCD(width=self.width, height=self.height, rotate=0)

    #         # --- cascade ---
    #         base_dir = os.path.dirname(os.path.abspath(__file__))
    #         cascade_path = os.path.join(base_dir, "haarcascade_frontalface_default.xml")
    #         self.face_cascade = cv2.CascadeClassifier(cascade_path)
    #         if self.face_cascade.empty():
    #             raise RuntimeError(f"Failed to load cascade: {cascade_path}")

    #         self.fps = 0.0

    #     def visualize_fps(self, image_bgra, fps: float):
    #         # cv2 text wants BGR/BGRA just fine
    #         fps_text = f"FPS = {fps:.1f}"
    #         cv2.putText(
    #             image_bgra,
    #             fps_text,
    #             (10, 20),
    #             cv2.FONT_HERSHEY_PLAIN,
    #             1.2,
    #             (0, 255, 0, 255),
    #             2
    #         )
    #         return image_bgra

    #     def run(self, target_fps=12):
    #         """
    #         target_fps limits how fast we push frames over SPI.
    #         10-15 is realistic on many setups.
    #         """
    #         frame_period = 1.0 / target_fps
    #         last_time = time.time()

    #         try:
    #             while True:
    #                 t0 = time.time()

    #                 frame = self.camera.capture_array()  # BGRA-ish (XRGB8888)
    #                 # Make a copy if you want; capture_array already gives a new array usually.
    #                 frame_out = frame

    #                 # Face detection wants grayscale; convert BGRA -> GRAY safely
    #                 gray = cv2.cvtColor(frame_out, cv2.COLOR_BGRA2GRAY)

    #                 faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)

    #                 # Draw boxes
    #                 for (x, y, w, h) in faces:
    #                     cv2.rectangle(frame_out, (x, y), (x + w, y + h), (255, 0, 0, 255), 2)

    #                 # FPS estimate
    #                 now = time.time()
    #                 dt_fps = now - last_time
    #                 last_time = now
    #                 if dt_fps > 0:
    #                     self.fps = 1.0 / dt_fps

    #                 frame_out = self.visualize_fps(frame_out, self.fps)

    #                 # Push to LCD
    #                 self.lcd.show_bgra_frame(frame_out)

    #                 # Cap update rate
    #                 elapsed = time.time() - t0
    #                 sleep_time = frame_period - elapsed
    #                 if sleep_time > 0:
    #                     time.sleep(sleep_time)

    #         except KeyboardInterrupt:
    #             pass
    #         finally:
    #             self.camera.close()


    # # peripherals/display.py

class LCD:
    def __init__(self, width=320, height=240, rotate=0, dc=24, rst=25, bus_speed_hz=52000000):
        self.width = width
        self.height = height

        self.serial = spi(device=0, port=0, gpio_DC=dc, gpio_RST=rst, bus_speed_hz=bus_speed_hz)
        self.device = ili9341(self.serial, width=width, height=height, rotate=rotate)

        self.font_big = self._load_font(72)
        self.font_medium= self._load_font(48)
        self.font_small = self._load_font(20)

        self.frames = []
        self.frame_count = 0

        self.gif_frame_index = 0

    def _load_font(self, size):
        # Try common fonts; fall back to default if needed
        for p in [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        ]:
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
        return ImageFont.load_default()

    def show_timer(self, seconds_left: int, title: str = "LOCKED IN"):
        """
        White background, black text.
        """
        seconds_left = max(0, int(seconds_left))
        mm = seconds_left // 60
        ss = seconds_left % 60
        tstr = f"{mm:02d}:{ss:02d}"

        img = Image.new("RGB", (self.width, self.height), "white")
        draw = ImageDraw.Draw(img)

        # Title (top)
        draw.text((12, 10), title, font=self.font_small, fill="black")

        # Center time
        bbox = draw.textbbox((0, 0), tstr, font=self.font_big)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        x = (self.width - tw) // 2
        y = (self.height - th) // 2 - 10
        draw.text((x, y), tstr, font=self.font_big, fill="black")

        # Footer
        draw.text((12, self.height - 28), "Press Ctrl+C to stop", font=self.font_small, fill="black")

        self.device.display(img)

    def show_warning(self, seconds_left: int, title: str = "GIT OVER HERE >:("):
        """
        White background, black text.
        """
        seconds_left = max(0, int(seconds_left))
        mm = seconds_left // 60
        ss = seconds_left % 60
        tstr = f"{mm:02d}:{ss:02d}"

        img = Image.new("RGB", (self.width, self.height), "red")
        draw = ImageDraw.Draw(img)

        # Title (top)
        draw.text((12, 10), title, font=self.font_small, fill="white")

        # Center time
        bbox = draw.textbbox((0, 0), tstr, font=self.font_big)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        x = (self.width - tw) // 2
        y = (self.height - th) // 2 - 10
        draw.text((x, y), tstr, font=self.font_big, fill="white")

        # Footer
        draw.text((12, self.height - 28), "Press Ctrl+C to stop", font=self.font_small, fill="black")

        self.device.display(img)

    def show_clock(self, title: str = "THE ALL-CONSUMING-CLOCK"):
        """
        Shows the current time: black text over white background.
        """
        current_time = datetime.now().time()

        img = Image.new("RGB", (self.width, self.height), "white")
        draw = ImageDraw.Draw(img)

        # Title (top)
        draw.text((12, 10), title, font=self.font_small, fill="black")

        # Center time
        bbox = draw.textbbox((0, 0), current_time, font=self.font_big)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        x = (self.width - tw) // 2
        y = (self.height - th) // 2 - 10
        draw.text((x, y), current_time, font=self.font_big, fill="black")

        # Footer
        draw.text((12, self.height - 28), "Press Ctrl+C to stop", font=self.font_small, fill="black")

        self.device.display(img)

    def load_gif(self, gif_path):  # Rename + non-blocking
        """LOADS frames only - doesn't display"""
        self.frames.clear()
        try:
            gif = Image.open(gif_path)
            for frame in ImageSequence.Iterator(gif):
                frame_rgb = frame.convert("RGB").resize((self.width, self.height))
                self.frames.append(frame_rgb)
            self.frame_count = len(self.frames)
            print(f"✅ Loaded {self.frame_count} frames from {gif_path}")
        except Exception as e:
            print(f"❌ GIF error: {e}")
            self.frames.clear()
            self.frame_count = 0

    def play_gif_frame(self):  # Single frame
        if self.frame_count > 0:
            self.device.display(self.frames[self.gif_frame_index])
            self.gif_frame_index = (self.gif_frame_index + 1) % self.frame_count

# if __name__ == "__main__":

#     app = FaceDetectorLCD(width=320, height=240)
#     app.run(target_fps=12)