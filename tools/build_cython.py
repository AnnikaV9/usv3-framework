#
#  Script for building cython modules.
#

import os
try:
    from setuptools import setup, Extension
    from Cython.Build import cythonize

except ImportError:
    print("Run 'poetry install -E cython' to install dependencies required for building cython modules.")
    raise SystemExit


def find_cython_modules() -> list:
    ext_modules = []
    for root, _, files in os.walk("usv3/events"):
        for file in sorted(files):
            if file.endswith(".pyx"):
                ext_modules.append(Extension(f"{root.replace('/', '.')}.{file.removesuffix(".pyx")}", [os.path.join(root, file)]))

    return ext_modules


setup(
    name="usv3 cython modules",
    ext_modules=cythonize(find_cython_modules(), language_level="3"),
)
