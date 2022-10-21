from distutils.sysconfig import get_python_lib
from pathlib import Path

from setuptools import setup

CURRENT_DIR = Path(__file__).parent
SITE_PACKAGES = get_python_lib()


with open(f"{SITE_PACKAGES}/sublist_loader.pth", "w") as f:
    f.write("import sublist")


def get_long_description():
    readme_md = CURRENT_DIR / "README.md"
    with open(readme_md, encoding="utf8") as ld_file:
        return ld_file.read()


setup(
    name="sublist",
    version="0.0.1",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    description="A new list slice feature that allows you to create sub-lists.",
    keywords=["slice"],
    author="Furkan Onder",
    author_email="furkanonder@protonmail.com",
    url="https://github.com/furkanonder/sublist/",
    license="MIT",
    python_requires=">=3.9",
    py_modules=["sublist"],
    install_requires=[],
    extras_require={},
    zip_safe=False,
    include_package_data=False,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Unix",
        "Operating System :: Microsoft :: Windows",
    ],
)
