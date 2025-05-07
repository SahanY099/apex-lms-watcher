import json
from typing import NoReturn

from auth import auth_request
from data_types import Paper


API_URL = "https://apexonline.lk/api/v1/exams/get-merged-exams"
FAKE_DATA_FILE_PATH = "bin/merged_exams.json"


def fetch_essay_data():
    FAKE = False
    if FAKE:
        # Read and load the JSON data
        with open(FAKE_DATA_FILE_PATH, "r") as file:
            data = json.load(file)
        return data
    else:
        try:
            response = auth_request.post(API_URL)
            response.raise_for_status()  # Raise an exception for HTTP errors

            return response.json()

        except auth_request.exceptions.RequestException as e:
            print(f"Error checking API: {e}")


def check_for_essay(paper_number: int) -> Paper | NoReturn:
    """
    Check the API for a specific essay paper.

    Args:
        paper_number: The number of the essay paper to search for.

    Returns:
        A Paper object with the name, type, unlocks_at, and expires_at of the matching essay paper.
        If no matching paper is found, prints an error message and returns nothing (NoReturn).
    """
    try:
        exams = fetch_essay_data()
        paper = None

        for exam in exams:
            exam_data = exam.get("exam_id", {})
            exam_name = exam_data.get("exam_name", "").lower()

            if paper_number in exam_name:
                paper = exam_data
                break

        return Paper(
            name=paper.get("exam_name"),
            type=Paper.PaperType.ESSAY,
            unlocks_at=paper.get("exam_unlocks_at"),
            expires_at=paper.get("exam_expires_at"),
        )

    except Exception as e:
        print(str(e))
