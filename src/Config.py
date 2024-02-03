import os


class Config:
    UPLOAD_EXTENSIONS = ("pdf", "txt")
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
    TEXT_DIR = os.getenv("TEXT_DIR", UPLOAD_DIR + "/extracted_text")
