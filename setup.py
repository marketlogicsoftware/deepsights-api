# Copyright 2024 Market Logic Software AG. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This module defines the packaging of deepsights-api.
"""

import io
import os
from setuptools import setup, find_packages


package_root = os.path.abspath(os.path.dirname(__file__))

readme_filename = os.path.join(package_root, "README.md")
with io.open(readme_filename, encoding="utf-8") as readme_file:
    readme = readme_file.read()

reqs_filename = os.path.join(package_root, "requirements.txt")
with io.open(reqs_filename, encoding="utf-8") as reqs_file:
    reqs = reqs_file.read().splitlines()

setup(
    name="deepsights-api",
    version="1.2.1",
    author="Market Logic Software",
    author_email="info@marketlogicsoftware.com",
    description="Python library for the DeepSights APIs",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/marketlogicsoftware/deepsights-api",
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    install_requires=reqs,
    license="Apache 2.0",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    project_urls={
        "Documentation": "https://marketlogicsoftware.github.io/deepsights-api/"
    },
)
