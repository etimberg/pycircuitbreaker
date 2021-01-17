import os
import os.path
from setuptools import setup, find_packages

thisdir = os.path.abspath(os.path.dirname(__file__))
version = open(os.path.join(thisdir, "pycircuitbreaker", "VERSION")).read().strip()


def readme():
    with open("README.md", "r", encoding="UTF-8") as f:
        return f.read()


setup(
    name="pycircuitbreaker",
    author="Evert Timberg",
    author_email="evert@everttimberg.io",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="Python implementation of the Circuit Breaker Pattern",
    extras_require={
        "test": [
            "pytest>=5.3",
            "pytest-cov",
        ]
    },
    license="MIT",
    long_description=readme(),
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["tests", "tests.*"]),
    package_data={"": ["VERSION"]},
    platforms="any",
    url="https://github.com/etimberg/pycircuitbreaker",
    version=version,
    zip_safe=False,
)
