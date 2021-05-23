import io
import os
from setuptools import setup, find_packages

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(CURRENT_DIR, "README.md"), "r", encoding="utf-8") as f:
    README = f.read()

with io.open(os.path.join(CURRENT_DIR, "requirements.txt"), "r", encoding="utf-8") as f:
    DEPENDENCIES = [line.strip() for line in f.readlines()]

setup(
    name="housecarl",
    version="0.0.1",
    packages=find_packages(),
    install_requires=DEPENDENCIES,
    author="Robert Reed",
    author_email="robert.mc.reed@gmail.com",
    description="Carl will monitor a video feed and send you push notifications if events are detected.",
    long_description=README,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords=[
        "Wyze",
        "OpenCV",
        "video",
        "person detection",
        "object detection",
        "yolo",
        "mobilenet",
        "pushover"
        "Google Coral",
        "Raspberry Pi"
    ],
    python_requires=">=3.6",
    scripts=["bin/carl"],
    url="https://github.com/RobertMcReed/housecarl"
)
