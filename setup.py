from setuptools import setup
from setuptools import find_packages

about = {}
with open("hzy/_version.py") as fp:
    exec(fp.read(), about)

setup(
    name="hzy",
    version=about["__version__"],
    python_requires=">=3.11",
    description="Emulated input for Wayland in python",
    long_description="Emulated input for Wayland in python empowered by libei c lib",
    url="https://github.com/Hadhzy/hzy",
    license="Apache 2.0",
    packages=["hzy"],
    author="Hadhzy Organisation"
)
