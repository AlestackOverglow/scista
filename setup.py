from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="scista",
    version="0.1.2",
    author="AlestackOverglow",
    author_email="alestackoverglow@proton.me",
    description="A library for fetching scientific articles from various sources",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AlestackOverglow/scista",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "urllib3>=1.26.0",
    ],
) 