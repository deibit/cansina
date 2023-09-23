from setuptools import setup, find_packages

setup(
    name="cansina",
    version="1.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "cansina=cansina.cansina:__main__",
        ],
    },
    install_requires=[
        "requests",
    ],
    include_package_data=True,
)
