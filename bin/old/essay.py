import time
import json
from datetime import datetime
import sys
import os
from playsound import playsound
import webbrowser

from auth import AuthenticatedSession

requests = AuthenticatedSession("", "")

# Configuration
API_URL = "https://apexonline.lk/api/v1/exams/get-merged-exams"
SEARCH_TERM = "32"  # Case insensitive search term
CHECK_INTERVAL = 60  # Check every 60 seconds
NOTIFICATION_SOUND_FILE = "alarm.mp3"  # You'll need to provide this file
OPEN_BROWSER = True  # Set to True to open browser when found

# Create a file to log found exams to avoid duplicate notifications
LOG_FILE = "found_exams.json"


def setup():
    """Set up the environment."""
    # Create log file if it doesn't exist
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            json.dump([], f)

    # Check if notification sound exists
    if not os.path.exists(NOTIFICATION_SOUND_FILE):
        print(
            f"Warning: Notification sound file '{NOTIFICATION_SOUND_FILE}' not found."
        )
        print("The script will still run, but won't play a sound notification.")


def get_previously_found_exams():
    """Read the previously found exams from the log file."""
    try:
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_found_exam(exam_id):
    """Save a found exam ID to the log file."""
    found_exams = get_previously_found_exams()
    if exam_id not in found_exams:
        found_exams.append(exam_id)
        with open(LOG_FILE, "w") as f:
            json.dump(found_exams, f)


def check_for_essay():
    """Check the API for Pet 31 exams."""
    try:
        response = requests.post(API_URL)
        response.raise_for_status()  # Raise an exception for HTTP errors

        exams = response.json()
        found_exams = []

        for exam in exams:
            exam_data = exam.get("exam_id", {})
            exam_name = exam_data.get("exam_name", "").lower()
            exam_id = exam_data.get("id")

            if SEARCH_TERM in exam_name and exam_id:
                found_exams.append(
                    {
                        "id": exam_id,
                        "name": exam_data.get("exam_name"),
                        "unlocks_at": exam_data.get("exam_unlocks_at"),
                    }
                )

        return found_exams

    except requests.exceptions.RequestException as e:
        print(f"Error checking API: {e}")
        return []


def notify(exam):
    """Notify the user about a found exam."""
    print("\n" + "=" * 60)
    print(
        f"🔔 FOUND PET 31 EXAM! - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    print(f"Exam Name: {exam['name']}")
    print(f"Exam ID: {exam['id']}")
    print(f"Unlocks at: {exam['unlocks_at']}")
    print(f"Expires at: {exam['expires_at']}")
    print("=" * 60 + "\n")

    # Play notification sound if available
    try:
        if os.path.exists(NOTIFICATION_SOUND_FILE):
            playsound(NOTIFICATION_SOUND_FILE)
    except Exception as e:
        print(f"Failed to play notification sound: {e}")

    # Open browser
    if OPEN_BROWSER:
        try:
            webbrowser.open("https://apexonline.lk/dashboard")
        except Exception as e:
            print(f"Failed to open browser: {e}")


def main():
    """Main function to continuously check for Pet 31 exams."""
    setup()
    previously_found = get_previously_found_exams()

    print(f"Starting Pet 31 exam watcher...")
    print(
        f"Checking for exams containing '{SEARCH_TERM}' every {CHECK_INTERVAL} seconds..."
    )
    print(f"Press Ctrl+C to stop the script.")

    try:
        check_count = 0
        while True:
            check_count += 1
            current_time = datetime.now().strftime("%H:%M:%S")

            # Show a periodic heartbeat to indicate the script is still running
            sys.stdout.write(
                f"\rLast checked at {current_time} (#{check_count})..."
            )
            sys.stdout.flush()

            found_exams = check_for_essay()

            for exam in found_exams:
                exam_id = exam["id"]
                if exam_id not in previously_found:
                    notify(exam)
                    save_found_exam(exam_id)
                    previously_found.append(exam_id)

            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        print("\nStopping Pet 31 exam watcher...")
        sys.exit(0)


if __name__ == "__main__":
    main()
