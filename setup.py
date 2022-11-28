import re
from pathlib import Path

from setuptools import setup

home = Path(__file__).parent
readme = home / "README.rst"


def get_version():
    regex = re.compile(r'__version__ = "(?P<version>.+)"', re.M)
    match = regex.search((home / "async_retrying.py").read_text())
    return match.group("version")


setup(
    name="async_retrying",
    version=get_version(),
    author="OCEAN S.A.",
    author_email="osf@ocean.io",
    url="https://github.com/wikibusiness/async_retrying",
    description="Simple retrying for asyncio",
    long_description=readme.read_text(),
    install_requires=[
        "async_timeout",
    ],
    extras_require={
        ':python_version=="3.5"': ["asyncio"],
    },
    py_modules=["async_retrying"],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    keywords=["asyncio", "retrying"],
)
