from setuptools import setup, find_packages

from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="cansina",
    version="0.9",
    description="Web Content Discovery Tool",
    author="David Garcia",
    author_email="daganu@gmail.com",
    url="https://github.com/deibit/cansina",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "cansina=cansina.main:__main__",
        ],
    },
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=["requests", "asciitree"],
    package_data={"cansina.utils": ["*.txt"]},
    keywords=["pentesting", "cybersecurity", "websecurity"],
)
