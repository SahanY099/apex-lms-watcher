import os
from datetime import datetime
from enum import Enum
from typing import ClassVar, List, Optional

import dateutil.parser
from InquirerPy import inquirer
from pydantic import (
    BaseModel,
    Field,
    field_serializer,
    field_validator,
)
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    YamlConfigSettingsSource,
)

CONFIG_INQUIRERS = {
    "download_folder": inquirer.text(message="Download folder:"),
    "notification_sound_file": inquirer.text(
        message="Notification sound file:", default="alarm.mp3"
    ),
    "username": inquirer.text(message="Username:"),
    "password": inquirer.text(message="Password:"),
}


class BaseSettingsSingleton(BaseSettings):
    _instance: ClassVar[Optional["BaseSettingsSingleton"]] = None
    _is_initialized: ClassVar[bool] = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, *args, **kwargs):
        if self._is_initialized:
            return
        super().__init__(*args, **kwargs)
        self.__class__._is_initialized = True

    @classmethod
    def clear_singleton(cls):
        cls._instance = None
        cls._is_initialized = False


class Config(BaseSettingsSingleton):
    config_file_name: ClassVar[str] = "config.yaml"

    download_folder: Optional[str] = None
    notification_sound_file: Optional[str] = None

    username: Optional[str] = None
    password: Optional[str] = None

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ):
        # Only use YAML as the source
        return (YamlConfigSettingsSource(settings_cls, "config.yaml"),)

    @field_validator("download_folder", mode="plain")
    @classmethod
    def validate_download_folder(cls, value):
        if not value:
            value = CONFIG_INQUIRERS["download_folder"].execute()
        os.makedirs(value, exist_ok=True)
        return value

    @field_validator("notification_sound_file", mode="plain")
    @classmethod
    def validate_notification_sound_file(cls, value):
        if not value:
            value = CONFIG_INQUIRERS["notification_sound_file"].execute()
        if not value.endswith(".mp3"):
            raise ValueError(f"Notification sound must be an MP3 file: {value}")
        if not os.path.exists(value):
            print(f"Warning: Notification sound file '{value}' not found.")
            print(
                "The script will still run, but won't play a sound notification."
            )
        return value

    @field_validator("username", mode="plain")
    @classmethod
    def validate_username(cls, value):
        if not value:
            value = CONFIG_INQUIRERS["username"].execute()
        return value

    @field_validator("password", mode="plain")
    @classmethod
    def validate_password(cls, value):
        if not value:
            value = CONFIG_INQUIRERS["password"].execute()
        return value


class Material(BaseModel):
    """Pydantic model representing a material in a paper."""

    name: Optional[str] = None
    download_link: Optional[str] = None

    @staticmethod
    def get_paper_materials(materials_list: List[dict]) -> List["Material"]:
        """
        Transform paper materials data into the required format.

        Args:
            materials_list: List of materials related to the paper

        Returns:
            Paper: Structured data about the paper materials
        """
        paper_materials: List[Material] = []

        for material in materials_list:
            if material.get("material_type") == "DOCUMENT":
                if not any(
                    m.download_link == material.get("user_link")
                    for m in paper_materials
                ):
                    paper_materials.append(
                        Material(
                            name=material.get("material_title"),
                            download_link=material.get("user_link"),
                        )
                    )
        return paper_materials


class Paper(BaseModel):
    class PaperType(str, Enum):
        """Enum for paper types."""

        MCQ = "MCQ"
        ESSAY = "ESSAY"

    """Pydantic model representing a paper with its materials."""
    id: Optional[str] = None
    name: Optional[str] = None
    type: Optional[PaperType] = None
    unlocks_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    materials: Optional[List[Material]] = Field(default_factory=list)

    @field_validator("unlocks_at", "expires_at", mode="plain")
    def parse_datetime_fields(cls, value):
        if isinstance(value, str):
            try:
                return dateutil.parser.isoparse(value)
            except Exception:
                raise ValueError(f"Invalid datetime string: {value}")
        return value

    @field_serializer("unlocks_at", "expires_at", when_used="always")
    def format_datetime(cls, value: Optional[datetime]) -> Optional[str]:
        if isinstance(value, datetime):  # Ensure it's a datetime object
            return value.strftime("%Y-%m-%d %H:%M:%S")
        return None
