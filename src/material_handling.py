import os
from typing import List

import requests
from InquirerPy import inquirer
from InquirerPy.base.control import Choice

from data_types import Config, Material

config = Config()


def download_materials(materials: List[Material]):
    choices = []
    for material, index in zip(materials, range(len(materials))):
        choices.append(Choice(value=index, name=material.name))

    required_material_indexes = inquirer.select(
        message="Select required materials:", choices=choices, multiselect=True
    ).execute()

    for index in required_material_indexes:
        material = materials[index]
        response = requests.get(material.download_link)
        if response.status_code == 200:
            with open(
                f"{config.download_folder}/{material.name}.pdf", "wb"
            ) as f:
                f.write(response.content)
            print(f"✅ Downloaded: {material.name} to {config.download_folder}")
        else:
            print(f"❌ Failed to download: {material.name}")
