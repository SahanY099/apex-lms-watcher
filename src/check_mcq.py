import json
from typing import NoReturn

from .auth import auth_request
from .data_types import Material, Paper

API_URL = "https://apexonline.lk/api/v1/topics/get-lms-topics"
CLASS_ID = 2328
FAKE_DATA_FILE_PATH = "bin/curriculum.json"


def fetch_curriculum():
    FAKE = False
    if FAKE:
        # Read and load the JSON data
        with open(FAKE_DATA_FILE_PATH, "r") as file:
            data = json.load(file)
        return data
    else:
        try:
            response = auth_request.post(API_URL, data={"class_id": CLASS_ID})
            response.raise_for_status()

            data = response.json()
            return data
        except auth_request.exceptions.RequestException as e:
            print(f"Error checking API: {str(e)}")


def check_for_mcq(paper_number: int) -> Paper | NoReturn:
    """
    Check the topics API for PET MCQ entries with specific number

    Args:
        paper_number: The specific mcq paper number to search for (e.g., 30 for "PET 30 MCQ")
    """

    try:
        data = fetch_curriculum()

        # Look for PET with specific MCQ number in the response
        paper = None
        mcq_str = str(paper_number)  # Convert to string for comparison

        for item in data:
            title = item.get("topic_title", "").lower()
            # Check for titles containing both "pet" and the specific MCQ number
            if (
                "pet" in title
                and (mcq_str in title or f"{mcq_str} mcq" in title)
                and ("marking" not in title)
            ):
                for material in item.get("materials", []):
                    if material.get("material_type") == "DOCUMENT":
                        paper = item
                        break

        if paper:
            return Paper(
                id=str(paper.get("id")),
                name=paper.get("topic_title"),
                type=Paper.PaperType.MCQ,
                # unlocks_at=paper.get("unlocks_at"),
                # expires_at=paper.get("expires_at"),
                materials=Material.get_paper_materials(paper.get("materials")),
            )
    except Exception as e:
        print(str(e))
