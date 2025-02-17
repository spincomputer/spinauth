from setuptools import setup, find_packages

setup(
    name="spinauth",
    version="0.1.0",
    description="A reusable authentication verifier for projects building on SPIN",
    author="Hilal Agil",
    author_email="hilaal@gmail.com",
    url="https://github.com/spincomputer/spinauth",  # if hosted on GitHub
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "requests",
        "python-jose",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
