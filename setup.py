from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="amit",
    version="0.4",
    description="A pentest enumeration framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://github.com/polyedre/amit",
    author="Lucas Henry",
    author_email="lucas.henry@enseirb-matmeca.fr",
    license="GPL",
    scripts=["bin/amit"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: OS Independent",
    ],
    packages=["amit"],
    zip_safe=False,
)
