import os
import threading
import webbrowser
from datetime import datetime

from InquirerPy import inquirer
from playsound3 import playsound

from data_types import Config, Paper
from material_handling import download_materials

config = Config()
OPEN_BROWSER = False  # Set to True to open browser when found


def notify(paper: Paper):
    """Notify the user about a found paper."""
    print("\n" + "=" * 60)
    print(
        f"🔔 Found {paper.name} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    if paper.materials:
        print(f"No. of materials: {len(paper.materials)}")
    else:
        print("No materials available.")
    print(f"Unlocks at: {paper.unlocks_at}")
    print(f"Expires at: {paper.unlocks_at}")
    print("=" * 60 + "\n")

    # Play notification sound if available
    def play_notification():
        try:
            if os.path.exists(config.notification_sound_file):
                playsound(config.notification_sound_file)
        except Exception as e:
            print(f"Failed to play notification sound: {e}")

    threading.Thread(target=play_notification, daemon=True).start()

    if len(paper.materials) > 0:
        proceed_download = inquirer.confirm(
            message="Do you want to download materials?", default=True
        ).execute()

        if proceed_download:
            download_materials(paper.materials)

    # Open browser
    if OPEN_BROWSER:
        try:
            for material in paper.materials:
                webbrowser.open(material["user_link"])
        except Exception as e:
            print(f"Failed to open browser: {e}")
