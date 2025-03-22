from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ossfuzz_module",
    version="0.1.0",
    author="OSS-Fuzz API Contributor (Shashank Shekhar Singh)",
    author_email="ShashankShekharSingh1205@gmail.com",
    description="Python module for interacting with OSS-Fuzz services",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/ossfuzz_module",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Topic :: Security",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "pandas>=1.0.0",
        "pyyaml>=5.1",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "black>=20.8b1",
            "isort>=5.6.0",
            "mypy>=0.800",
            "flake8>=3.8.0",
        ],
    },
) 