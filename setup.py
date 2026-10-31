#!/usr/bin/env python3

from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / "README").read_text(encoding="utf-8")

setup(
    name="pretbuild",
    version="0.1.0",
    description="A build tool, setup tool and runner",
    long_description = long_description,
    long_description_content_type="text/plain",
    url="https://github.com/georgek-dev/pret",
    author="Georg K.",
    author_email="gk_coder@icloud.com",
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "pret=pretbuild.main:main",
            "pret-build=pretbuild.build.main:build_main",
            "pret-clean=pretbuild.clean.main:clean_main",
            "pret-pybuild=pretbuild.pybuild.main:cli_main"
        ],
    },
    install_requires=[
        'tomli >= 1.1.0; python_version < "3.11"',
    ],
    project_urls={
        "Issues": "https://github.com/georgek-dev/pret/issues",
        "Source": "https://github.com/georgek-dev/pret"
    }
)
