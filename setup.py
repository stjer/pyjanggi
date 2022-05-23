from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="janggi",
    version="0.9.19",
    author="Sungho Cho",
    author_email="didog9595@gmail.com",
    description="Python library for Korean chess Janggi",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sungho-cho/pyjanggi",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=["janggi", "janggi/base", "janggi/game", "janggi/ui", "janggi/proto"],
    include_package_data=True,
    python_requires=">=3.6",
    install_requires=["termcolor==1.1.0", "pygame==2.1.2"],
)
