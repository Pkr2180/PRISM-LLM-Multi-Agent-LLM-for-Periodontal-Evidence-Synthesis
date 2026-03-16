from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="prism-llm",
    version="1.0.0",
    author="PRISM-LLM Team",
    description="Periodontal Regeneration Intelligence for Systematic Meta-benchmarking",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/[username]/prism-llm",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={"console_scripts": ["prism-llm=src.cli:main"]},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
    ],
)
