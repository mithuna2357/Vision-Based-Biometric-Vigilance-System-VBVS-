"""Audio alert module for the Eye Monitor application."""

import os
import threading
import time
try:
    import winsound
except ImportError:
    pass

import pygame

class AudioAlert:
    """Handles playing audio alerts continuously with fallback logic."""

    def __init__(self, filename="fahh.mp3"):
        self.filename = filename
        self.is_initialized = False
        self.is_beeping = False
        self.beep_thread = None
        try:
            pygame.mixer.init()
            self.is_initialized = True
        except pygame.error as e:
            print(f"Warning: Could not initialize pygame mixer: {e}")

    def play(self):
        """Play the alarm sound indefinitely."""
        if not self.is_initialized or not os.path.exists(self.filename):
            print(f"Warning: Audio file {self.filename} not found. Fallback continuous beep.")
            if not self.is_beeping:
                self.is_beeping = True
                self.beep_thread = threading.Thread(target=self._fallback_beep_loop, daemon=True)
                self.beep_thread.start()
            return
            
        try:
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.load(self.filename)
                pygame.mixer.music.play(-1) # Loop indefinitely
        except pygame.error as e:
            print(f"Error playing audio: {e}")
            if not self.is_beeping:
                self.is_beeping = True
                self.beep_thread = threading.Thread(target=self._fallback_beep_loop, daemon=True)
                self.beep_thread.start()

    def stop(self):
        """Stop the currently playing alarm sound."""
        if self.is_initialized:
            pygame.mixer.music.stop()
        self.is_beeping = False

    def _fallback_beep_loop(self):
        """Fallback thread that loops a system beep."""
        while self.is_beeping:
            try:
                winsound.Beep(1000, 500) # 1000 Hz for 0.5s
            except NameError:
                print('\a')
            time.sleep(0.5)
