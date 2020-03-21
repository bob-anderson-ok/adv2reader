from setuptools import setup
import pathlib
from Adv2 import Version


VERSION = Version.version()

KEYWORDS = ["ADV file reader", 'Astro Digital Video version 2 file reader']

CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Science/Research",
    "Natural Language :: English",
    "License :: OSI Approved :: MIT License",
    "Operating System :: MacOS :: MacOS X",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: POSIX :: Linux",
    "Programming Language :: Python :: 3.7",
    "Topic :: Scientific/Engineering",
]

INSTALL_REQUIRES = ['numpy']

HERE = pathlib.Path.cwd()

README = (HERE / "README.md").read_text()

setup(
    name="Adv2",
    python_requires='>=3.7',
    description='Adv2reader reads version 2 Astro Digital Video files.',
    license='License :: OSI Approved :: MIT License',
    url=r'https://github.com/bob-anderson-ok/adv2reader',
    version=VERSION,
    author='Bob Anderson',
    author_email='bob.anderson.ok@gmail.com',
    maintainer='Bob Anderson',
    maintainer_email='bob.anderson.ok@gmail.com',
    keywords=KEYWORDS,
    long_description=README,
    long_description_content_type="text/markdown",
    packages=["Adv2"],
    include_package_data=True,
    classifiers=CLASSIFIERS,
    install_requires=INSTALL_REQUIRES,
)
