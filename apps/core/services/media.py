import os
import uuid
from pathlib import Path

from fastapi import UploadFile

from config.database import DatabaseManager
from config.settings import MEDIA_DIR

# TODO get this from settings.py
max_upload_size = 5


# TODO set permission to access media-directory and files
class MediaService:
    def __init__(self, parent_directory: str = "media", sub_directory: str | int = None):
        testing = DatabaseManager.get_testing_mode()
        if not testing:
            self.path = Path(f"{MEDIA_DIR}/{parent_directory}/{sub_directory}" if sub_directory else parent_directory)
        else:
            self.path = Path(
                f"{MEDIA_DIR}/test/{parent_directory}/{sub_directory}" if sub_directory else parent_directory)
        # self.path.mkdir(parents=True, exist_ok=True)

    def save_file(self, file: UploadFile):
        # TODO separate exceptions to a module in core app
        # Check if the file extension is allowed
        file_extension = self.get_file_extension(file)
        # if not self.is_allowed_extension(file_extension):
        #     raise HTTPException(status_code=400, detail="File type not allowed")

        # Check if the file size is within the allowed limit in MB
        # if self.get_file_size_mb(file) > max_upload_size:
        #     raise HTTPException(status_code=400, detail="File size exceeds the limit")

        # Generate a unique filename with a random string and date
        file_name = self.generate_unique_filename(file.filename)
        if not os.path.exists(self.path):
            os.makedirs(self.path, exist_ok=True)

            # for file in files:
        new_file = os.path.join(self.path, file_name)

        with open(new_file, 'wb') as f:
            f.write(file.file.read())

        # ======
        # with open(file_name, 'wb') as f:
        #     f.write(file.file.read())

        return file_name, file_extension

    def generate_unique_filename(self, filename: str) -> str:
        random_string = str(uuid.uuid4().hex)
        file_extension = filename.split('.')[-1]
        unique_filename = f"{random_string}.{file_extension}"
        return unique_filename

    @staticmethod
    def is_allowed_extension(extension: str) -> bool:
        allowed_extensions = {"jpg", "jpeg", "png", "gif", "mp4", "mov", "pdf"}
        return extension.lower() in allowed_extensions

    @staticmethod
    def get_file_extension(file: UploadFile) -> str:
        filename_parts = file.filename.split('.')
        return filename_parts[-1] if len(filename_parts) > 1 else ""

    @staticmethod
    def get_file_size_mb(file: UploadFile) -> float:
        file_size_bytes = file.file.seek(0, 2)
        return file_size_bytes / (1024 * 1024)  # Convert to MB
