"""Main Tkinter entry point for the Eye Monitor application."""
# pylint: disable=no-member

import tkinter as tk
from tkinter import scrolledtext
from tkinter import filedialog

from PIL import Image, ImageTk
import cv2

from vision_engine import VisionEngine
from audio_alert import AudioAlert
from logger_util import Logger

PASTEL_LAVENDER = "#E6E6FA"
PASTEL_PINK = "#FFB6C1"
LIGHT_BLUE = "#ADD8E6"
PURPLE = "#9370DB"
WHITE = "#FFFFFF"
BLACK = "#000000"
DARK_GREY = "#121212"

class EyeMonitorApp:
    """The main Tkinter GUI application class."""

    def __init__(self, app_root):
        self.root = app_root
        self.root.title("Eye Monitor Application - Pastel Edit")
        self.root.geometry("850x700")
        self.root.configure(bg=BLACK)

        self.audio = AudioAlert("fahh.mp3")
        self.logger = Logger("alert_history.csv")
        self.vision = VisionEngine(
            self.update_ui, self.trigger_alert, self.stop_alert, alert_threshold=60.0
        )

        self.btn_start = None
        self.btn_stop = None
        self.lbl_timer = None
        self.lbl_status = None
        self.history_text = None
        self.threshold_entry = None
        self.video_label = None

        self.setup_ui()
        self.refresh_history()

    def setup_ui(self):
        """Initializes all Tkinter UI components with the updated Pastel aesthetic."""
        font_body = ("Times New Roman", 12)
        font_header = ("Arial", 20, "bold") # Keeping main heading Arial for punchiness
        font_timer = ("Times New Roman", 15, "bold")

        # Main Title
        tk.Label(
            self.root, text="D O N ' T   N O D   O F F",
            bg=BLACK, fg=PASTEL_LAVENDER, font=font_header, pady=10
        ).pack()

        self.video_label = tk.Label(self.root, bg=BLACK)
        self.video_label.pack(pady=5)

        control_frame = tk.Frame(self.root, bg=BLACK)
        control_frame.pack(pady=10)

        tk.Label(
            control_frame, text="Alert Threshold (s):",
            bg=BLACK, fg=WHITE, font=font_body
        ).pack(side=tk.LEFT, padx=5)

        self.threshold_entry = tk.Entry(
            control_frame, width=5, bg=DARK_GREY, fg=LIGHT_BLUE,
            font=font_body, relief="flat", insertbackground=LIGHT_BLUE
        )
        self.threshold_entry.insert(0, "60.0")
        self.threshold_entry.pack(side=tk.LEFT, padx=5)

        self.btn_browse = tk.Button(
            control_frame, text="Select Audio...", command=self.browse_audio,
            bg=PURPLE, fg=WHITE, font=font_body, relief="flat",
            activebackground="#7A28CB", activeforeground=WHITE, padx=10
        )
        self.btn_browse.pack(side=tk.LEFT, padx=10)

        self.btn_start = tk.Button(
            control_frame, text="Start Monitoring", command=self.start_monitoring,
            width=15, bg=LIGHT_BLUE, fg=BLACK, font=font_body, relief="flat",
            activebackground="#88C0D0", activeforeground=BLACK
        )
        self.btn_start.pack(side=tk.LEFT, padx=10)

        self.btn_stop = tk.Button(
            control_frame, text="Stop Monitoring", command=self.stop_monitoring,
            width=15, bg=PASTEL_PINK, fg=BLACK, font=font_body, relief="flat", state=tk.DISABLED,
            activebackground="#FF8DA1", activeforeground=BLACK
        )
        self.btn_stop.pack(side=tk.LEFT, padx=10)

        self.lbl_timer = tk.Label(
            self.root, text="Closed Duration: 0.0s",
            bg=BLACK, fg=LIGHT_BLUE, font=font_timer
        )
        self.lbl_timer.pack(pady=5)

        self.lbl_status = tk.Label(
            self.root, text="Status: Stopped",
            bg=BLACK, fg=PASTEL_LAVENDER, font=font_body
        )
        self.lbl_status.pack()

        history_header_frame = tk.Frame(self.root, bg=BLACK)
        history_header_frame.pack(pady=(15, 5), fill=tk.X, padx=80)

        tk.Label(
            history_header_frame, text="Alert History (Date & Time):",
            bg=BLACK, fg=WHITE, font=font_body
        ).pack(side=tk.LEFT)
        tk.Button(
            history_header_frame, text="Clear History", command=self.clear_history,
            bg="#1A1A1A", fg=PASTEL_LAVENDER, font=font_body, relief="flat",
            activebackground="#333333", activeforeground=PASTEL_LAVENDER, padx=10
        ).pack(side=tk.RIGHT)

        self.history_text = scrolledtext.ScrolledText(
            self.root, height=10, width=90,
            bg=DARK_GREY, fg=WHITE, font=("Times New Roman", 11),
            relief="flat", insertbackground=WHITE, highlightthickness=0
        )
        self.history_text.pack(pady=5)

    def browse_audio(self):
        """Opens a file dialog to select an audio file."""
        filepath = filedialog.askopenfilename(
            title="Select Alert Audio",
            filetypes=(
                ("Audio Files", "*.mp3 *.wav *.ogg"),
                ("All Files", "*.*")
            )
        )
        if filepath:
            self.audio.filename = filepath
            filename = filepath.split('/')[-1]
            msg = f"Selected custom audio file: {filename}"
            timestamp = self.logger.log_event(msg)
            self._append_history(f"{timestamp} - {msg}")

    def start_monitoring(self):
        """Starts the vision engine monitoring."""
        try:
            threshold = float(self.threshold_entry.get())
        except ValueError:
            threshold = 60.0
            self.threshold_entry.delete(0, tk.END)
            self.threshold_entry.insert(0, "60.0")
        self.vision.alert_threshold = threshold

        self.btn_start.config(state=tk.DISABLED, bg="#1A1A1A", fg=WHITE)
        self.btn_stop.config(state=tk.NORMAL, bg=PASTEL_PINK, fg=BLACK)
        self.lbl_status.config(text="Status: Monitoring...", fg=LIGHT_BLUE)
        self.vision.start()

    def stop_monitoring(self):
        """Stops the vision engine monitoring."""
        self.btn_start.config(state=tk.NORMAL, bg=LIGHT_BLUE, fg=BLACK)
        self.btn_stop.config(state=tk.DISABLED, bg=PASTEL_PINK, fg="#888888")
        self.lbl_status.config(text="Status: Stopped", fg=PASTEL_LAVENDER)
        self.vision.stop()
        self.audio.stop()
        self.video_label.config(image='')
        self.lbl_timer.config(text="Closed Duration: 0.0s", fg=LIGHT_BLUE)

    def trigger_alert(self, duration):
        """Callback to start the alarm when threshold is reached."""
        self.audio.play()
        msg = f"Alert! Eyes closed for {duration:.1f} seconds"
        timestamp = self.logger.log_event(msg)
        self.root.after(0, self._append_history, f"{timestamp} - {msg}")

    def stop_alert(self):
        """Callback to stop the alarm."""
        self.audio.stop()

    def _append_history(self, msg):
        """Thread-safe UI update for history log."""
        self.history_text.insert(tk.END, msg + "\n")
        self.history_text.see(tk.END)

    def refresh_history(self):
        """Reloads history from the CSV file into the UI textbox."""
        self.history_text.delete(1.0, tk.END)
        for h in self.logger.get_history():
            self.history_text.insert(tk.END, h + "\n")

    def clear_history(self):
        """Clears all history logs."""
        self.logger.clear_history()
        self.refresh_history()

    def update_ui(self, frame, stats):
        """Callback to update the GUI video frame and stats."""
        if frame is not None:
            cv_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(cv_img)
            # Resize slightly to fit the new aesthetic layout tighter
            pil_img = pil_img.resize((600, 450))
            tk_img = ImageTk.PhotoImage(image=pil_img)

            def set_image():
                self.video_label.tk_img = tk_img
                self.video_label.config(image=tk_img)
                self.lbl_timer.config(text=f"Closed Duration: {stats['closed_duration']:.1f}s")
                
                if stats['is_static_photo']:
                    self.lbl_status.config(text="Status: STATIC PHOTO DETECTED", fg=PASTEL_PINK)
                elif not stats['face_detected']:
                    self.lbl_status.config(text="Status: No Face Detected", fg=WHITE)
                else:
                    color = PASTEL_PINK if stats['ear'] < self.vision.ear_threshold else LIGHT_BLUE
                    self.lbl_status.config(
                        text=f"Status: Monitoring (EAR: {stats['ear']:.2f})", fg=color
                    )

            self.root.after(0, set_image)

    def on_closing(self):
        """Handle window close event."""
        self.stop_monitoring()
        self.root.destroy()

if __name__ == "__main__":
    main_app_root = tk.Tk()
    my_app = EyeMonitorApp(main_app_root)
    main_app_root.protocol("WM_DELETE_WINDOW", my_app.on_closing)
    main_app_root.mainloop()
