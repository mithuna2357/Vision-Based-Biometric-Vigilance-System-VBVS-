# Vision-Based Biometric Vigilance System (VBVS)

Real-time drowsiness monitoring using webcam video: **Eye Aspect Ratio (EAR)** from facial landmarks, a Tkinter GUI, CSV alert history, and customizable audio alerts.

**Repository:** [github.com/mithuna2357/Vision-Based-Biometric-Vigilance-System-VBVS-](https://github.com/mithuna2357/Vision-Based-Biometric-Vigilance-System-VBVS-)

---

## Built by

**Mithuna Somireddy**

---

## Features

- **EAR-based vigilance** — Eyes-closed duration tracked via MediaPipe Face Landmarker; alerts when closure exceeds a configurable threshold (seconds).
- **Live GUI** — Pastel-themed Tkinter interface with camera preview, closed-eye timer, and status (monitoring, no face, static-photo hint).
- **Persistent logging** — Alert events appended to `alert_history.csv` with timestamps; history shown in-app and clearable from the UI.
- **Audio alerts** — Default MP3 (`fahh.mp3`) or user-selected audio (MP3, WAV, OGG); pygame playback with Windows beep fallback if the file is missing.

---

## Requirements

- **Python** 3.9+ recommended  
- **Webcam** (default camera index `0`)
- **Model file** — `face_landmarker.task` must be present next to the application (bundled with this project).

---

## Installation

```bash
git clone https://github.com/mithuna2357/Vision-Based-Biometric-Vigilance-System-VBVS-.git
cd Vision-Based-Biometric-Vigilance-System-VBVS-
python -m venv .venv
```

**Windows (PowerShell):**

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**macOS / Linux:**

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Run

From the project directory (with the virtual environment activated):

```bash
python main.py
```

1. Optionally set **Alert Threshold (s)** — seconds eyes may stay closed before an alert (default `60.0`).
2. Optionally use **Select Audio...** to choose an alert sound.
3. Click **Start Monitoring**; use **Stop Monitoring** when finished.

---

## Project layout

| Path | Role |
|------|------|
| `main.py` | Tkinter app entry point |
| `vision_engine.py` | Camera thread, MediaPipe face landmarks, EAR + alert logic |
| `utils.py` | Eye landmark indices and `calculate_ear()` |
| `audio_alert.py` | pygame / fallback beep |
| `logger_util.py` | CSV alert history |
| `face_landmarker.task` | MediaPipe Face Landmarker model |
| `alert_history.csv` | Generated log (created/updated at runtime) |

---

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE).

---

## Author

**Mithuna Somireddy** — developer and maintainer.
