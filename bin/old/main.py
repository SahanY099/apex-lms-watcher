import argparse
import os
import sys
import time
import webbrowser
from datetime import datetime

from playsound3 import playsound

from auth import AuthenticatedSession

requests = AuthenticatedSession("", "")

NOTIFICATION_SOUND_FILE = "alarm.mp3"  # You'll need to provide this file
OPEN_BROWSER = True  # Set to True to open browser when found
CHECK_INTERVAL = 60  # Check every 60 seconds
API_URL = "https://apexonline.lk/api/v1/exams/get-merged-exams"


TYPE_MCQ = "mcq"
TYPE_ESSAY = "essay"


def check_for_mcq(exam_number: int):
    """
    Check the topics API for PET MCQ entries with specific number

    Args:
        mcq_number: The specific MCQ number to search for (e.g., 30 for "PET 30 MCQ")
        auth_token: Optional auth token for API requests
    """
    url = "https://apexonline.lk/api/v1/topics/get-lms-topics"

    try:
        response = requests.post(url, data={"class_id": 2328})

        # Check if response is valid JSON
        if response.status_code == 200:
            data = response.json()

            # Look for PET with specific MCQ number in the response
            exam = None
            exam_materials = None
            mcq_str = str(exam_number)  # Convert to string for comparison

            for item in data:
                title = item.get("topic_title", "").lower()
                # Check for titles containing both "pet" and the specific MCQ number
                if "pet" in title and (
                    mcq_str in title or f"{mcq_str} mcq" in title
                ):
                    exam = item
                    exam_materials = item.get("materials", {})
                    break

            if exam:
                return {
                    "id": exam.get("id"),
                    "name": exam.get("topic_title"),
                    "unlocks_at": exam_materials[0].get("unlock_timestamp"),
                    "expires_at": exam_materials[0].get("expire_timestamp"),
                    "material_link": exam_materials[0].get("user_link"),
                }

        else:
            print(f"Error: Received status code {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"Error checking API: {str(e)}")
        return False


def check_for_essay(exam_number: int):
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

            if exam_number in exam_name and exam_id:
                found_exams.append(
                    {
                        "id": exam_id,
                        "type": TYPE_ESSAY,
                        "name": exam_data.get("exam_name"),
                        "unlocks_at": exam_data.get("exam_unlocks_at"),
                        "expires_at": exam_data.get("exam_expires_at"),
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
            webbrowser.open(exam["material_link"])
        except Exception as e:
            print(f"Failed to open browser: {e}")


if __name__ == "__main__":
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(
        description="Monitor API for PET MCQ with specific number"
    )
    parser.add_argument(
        "mcq_number",
        type=int,
        help="The specific MCQ number to look for (e.g., 30)",
    )
    # parser.add_argument('--username', default="", help='API username')
    # parser.add_argument('--password', default="", help='API password')
    parser.add_argument(
        "--interval", type=int, default=60, help="Check interval in seconds"
    )
    parser.add_argument(
        "--max-checks", type=int, default=None, help="Maximum number of checks"
    )

    args = parser.parse_args()

    # username=args.username,
    # password=args.password,

    # Start monitoring with the specified MCQ number

    print("Starting PET exam watcher...")

    try:
        check_count = 0
        while True:
            check_count += 1
            current_time = datetime.now().strftime("%H:%M:%S")

            # Show a periodic heartbeat to indicate the script is still running

            exam = check_for_mcq(args.mcq_number)

            if exam:
                try:
                    notify(exam)
                    print("Exiting")
                    exit()
                except Exception as e:
                    print("found")
            else:
                sys.stdout.write(
                    f"\rLast checked at {current_time} (#{check_count})..."
                )
                sys.stdout.flush()
                time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        print("\nStopping PET exam watcher...")
        sys.exit(0)
