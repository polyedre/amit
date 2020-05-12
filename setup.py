from setuptools import setup

setup(
    name="amit",
    version="0.1",
    description="A pentest enumeration framework",
    url="http://github.com/polyedre/amit",
    author="Lucas Henry",
    author_email="lucas.henry@enseirb-matmeca.fr",
    license="GPL",
    scripts=["bin/amit"],
    packages=["amit"],
    zip_safe=False,
)
