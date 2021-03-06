#!/usr/bin/env python

from distutils.core import setup

setup(
    name="berbl-eval",
    version="0.1.0",
    description="Helpers for evaluating BERBL experiments",
    author="berbl",
    author_email="berbl@berbl.berbl",
    url="https://github.com/berbl-dev/berbl-eval",
    packages=[
        "berbl.eval"
    ],
    package_dir={"": "src"},
    install_requires=[
        "baycomp",
        "mlflow >=1.22",
        "numpy >=1.21.4",
        "pandas >=1.3.4",
        "pystan ==3.4.0",
    ])
