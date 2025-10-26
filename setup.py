from setuptools import setup, find_packages
import os

version = {}
with open(os.path.join("scripts", "version.py")) as f:
    exec(f.read(), version)

desc = "Merge paired FASTQ (gzip possible) files based on metadata, samples can belong to multiple groups, or merge all reads together into one forward and one reverse read."

with open("README.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()

import os
lib_folder = os.path.dirname(os.path.realpath(__file__))
requirement_path = f"{lib_folder}/requirements.txt"
install_requires = []
if os.path.isfile(requirement_path):
    with open(requirement_path) as f:
        install_requires = f.read().splitlines()

setup(
    name="Sample_grouping",
    version=version["__version__"],
    install_requires=install_requires,
    description=desc,
    long_description=long_description,
    long_description_content_type = "text/markdown",
    author="Santino Faack",
    author_email="santino_faack@gmx.de",
    license="GPL-3.0",
    packages=find_packages(),
    url="https://github.com/SantaMcCloud/Sample_grouping",
    scripts=[
        "script/reorder_reads.py"
    ],
)