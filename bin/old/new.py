import time
import argparse
import json
import urllib.request
import urllib.error
import ssl
from datetime import datetime


def monitor_exam(
    api_url,
    auth_token,
    exam_keyword,
    check_interval=60,
    id_param=None,
    post_data=None,
):
    """
    Monitor the API endpoint for a specific exam by name.

    Parameters:
    - api_url: The API URL to check
    - auth_token: Authorization token
    - exam_keyword: Keyword to search for in exam names
    - check_interval: Time between checks in seconds (default 60 seconds)
    - id_param: Optional ID parameter to add to the API request
    - post_data: Optional data to send with the POST request
    """
    headers = {"Authorization": auth_token, "Content-Type": "application/json"}

    # Prepare URL with ID parameter if provided
    if id_param:
        if "?" in api_url:
            url = f"{api_url}&id={id_param}"
        else:
            url = f"{api_url}?id={id_param}"
    else:
        url = api_url

    # Prepare POST data
    if post_data is None:
        post_data = {}

    encoded_data = json.dumps(post_data).encode("utf-8")

    print(f"Starting exam monitor...")
    print(f"Looking for exams containing: '{exam_keyword}'")
    print(f"Will check every {check_interval} seconds")
    print(f"API endpoint: {url}")
    print("=" * 50)

    check_count = 0

    try:
        while True:
            check_count += 1
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            try:
                print(
                    f"[{current_time}] Checking API (attempt #{check_count})..."
                )

                # Create an SSL context that doesn't verify certificates
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE

                # Create POST request with headers and data
                req = urllib.request.Request(
                    url, data=encoded_data, headers=headers, method="POST"
                )

                # Make the request with the SSL context
                with urllib.request.urlopen(
                    req, context=ssl_context
                ) as response:
                    response_data = response.read().decode("utf-8")
                    data = json.loads(response_data)

                    # Search for matching exams
                    matching_exams = []
                    for exam_data in data:
                        if (
                            "exam_id" in exam_data
                            and "exam_name" in exam_data["exam_id"]
                        ):
                            exam_name = exam_data["exam_id"][
                                "exam_name"
                            ].lower()
                            if exam_keyword.lower() in exam_name:
                                matching_exams.append(exam_data["exam_id"])

                    if matching_exams:
                        print("\n" + "!" * 50)
                        print(
                            f"EXAM FOUND! Found {len(matching_exams)} matching exam(s):"
                        )
                        for exam in matching_exams:
                            print("\n" + "-" * 40)
                            print(f"Exam Name: {exam['exam_name']}")
                            print(f"Exam Type: {exam['exam_type']}")
                            print(f"Status: {exam['status']}")

                            # Format dates nicely if they exist
                            if exam.get("exam_unlocks_at"):
                                unlocks_time = datetime.fromisoformat(
                                    exam["exam_unlocks_at"].replace(
                                        "Z", "+00:00"
                                    )
                                )
                                print(
                                    f"Unlocks At: {unlocks_time.strftime('%Y-%m-%d %H:%M:%S')} UTC"
                                )

                            if exam.get("exam_expires_at"):
                                expires_time = datetime.fromisoformat(
                                    exam["exam_expires_at"].replace(
                                        "Z", "+00:00"
                                    )
                                )
                                print(
                                    f"Expires At: {expires_time.strftime('%Y-%m-%d %H:%M:%S')} UTC"
                                )

                            print(
                                f"Duration: {exam.get('duration_in_hours', 0)} hours {exam.get('duration_in_minutes', 0)} minutes"
                            )
                            print(f"Total Marks: {exam.get('total_marks')}")
                            print("-" * 40)

                        print("!" * 50 + "\n")

                        # You could add additional notifications here (email, SMS, etc.)

                        # Ask if user wants to continue monitoring
                        user_input = input(
                            "Exam found! Continue monitoring? (y/n): "
                        )
                        if user_input.lower() != "y":
                            print("Monitoring stopped.")
                            break
                    else:
                        print(
                            f"No matching exams found. Waiting {check_interval} seconds before next check..."
                        )

            except urllib.error.URLError as e:
                print(f"Network error occurred: {str(e)}")
            except urllib.error.HTTPError as e:
                print(f"HTTP error occurred: {e.code} - {e.reason}")
            except json.JSONDecodeError:
                print("Error: Could not parse API response as JSON")
            except Exception as e:
                print(f"Unexpected error: {str(e)}")

            # Wait before next check
            time.sleep(check_interval)

    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")


if __name__ == "__main__":
    monitor_exam(
        api_url="https://apexonline.lk/api/v1/exams/get-merged-exams",
        auth_token="Bearer ",
        exam_keyword="32",
        check_interval=500,
        id_param=2328,
    )
