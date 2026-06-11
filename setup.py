from setuptools import setup, find_packages

setup(
    name="canfraudbench",
    version="0.1.0",
    description="A Canadian identity-fraud benchmark with OSFI E-23 governance mapping",
    packages=find_packages(),
    python_requires=">=3.8",
)
