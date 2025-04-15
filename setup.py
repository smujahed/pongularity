from setuptools import setup, find_packages

setup(
    name="pongularity",
    version="0.1.0",
    description="A simple implementation of the classic Pong game using Pygame",
    packages=find_packages(),
    install_requires=[
        "pygame>=2.5.2",
    ],
    entry_points={
        "console_scripts": [
            "pongularity=pongularity.__main__:main",
        ],
    },
) 