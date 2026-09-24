from setuptools import setup, find_packages

setup(
    name="Railoptix",
    version="1.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "Railoptix.ai=backend.run_render:start",
        ]
    }
)
