"""Logging utility for tracking alert events in the Eye Monitor application."""

import csv
import os
from datetime import datetime

class Logger:
    """Manages the CSV file for storing alert history."""

    def __init__(self, log_file="alert_history.csv"):
        self.log_file = log_file
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Event"])

    def log_event(self, event_message):
        """Logs a new event with the current date and time."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, event_message])
        return timestamp

    def get_history(self):
        """Reads and returns the complete alert history from the log file."""
        history = []
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader, None) # skip header
                for row in reader:
                    if len(row) >= 2:
                        history.append(f"{row[0]} - {row[1]}")
        return history

    def clear_history(self):
        """Clears the CSV log entirely, keeping only the headers."""
        with open(self.log_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "Event"])
