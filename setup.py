import setuptools
from setuptools import setup


LONG_DESC = """This is Nebix Trading Bot"""

setup(
    name="nebixbot",
    version="0.9.0",
    description="Nebix Trading Bot",
    long_description=LONG_DESC,
    long_description_content_type="text/plain",
    author="Nebix Team (Mohammad Salek)",
    url=" ",
    license="MIT",
    include_package_data=True,
    python_requires='>=3.8',
    packages=setuptools.find_packages(),
    entry_points={"console_scripts": ["nebixbot = nebixbot.__main__:main"]},
)
