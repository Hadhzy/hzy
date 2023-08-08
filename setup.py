from setuptools import setup
from setuptools import find_packages

about = {}
with open("hzy/_version.py") as fp:
    exec(fp.read(), about)

setup(
    name="hzy",
    version=about["__version__"],
    python_requires=">=3.11",
    description="Python wrapper around the c libei library",
    long_description="Emulated inputs for wayland in python empowered with CIBW",
    url="https://github.com/Hadhzy/hzy",
    license="Apache 2.0",
    packages=find_packages(where="hzy"),
    author="Hadhzy Organisation"
)
