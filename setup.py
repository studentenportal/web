import os
import subprocess

from setuptools import setup

# Fetch some information
VERSION = subprocess.check_output(["git", "rev-list", "HEAD", "--count"]).strip()

# Allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="studentenportal",
    version=VERSION,
    include_package_data=True,
    license="AGPLv3",
    description=r"open\OST Studentenportal",
    long_description="Dies ist ein re-launch des VSHSR Studentenportals. Es "
    + "hat das alte Portal im Frühling 2012 abgelöst und soll es in Sachen Ruhm"
    + "und Ehre weit überholen.",
    url="https://studentenportal.ch/",
    author="Danilo Bargen, Lukas Martinelli, Simon Schaefer",
    author_email="saspeed@gmail.com",
    classifiers=["Private :: Do Not Upload"],
)
