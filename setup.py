import setuptools
from setuptools import setup


LONG_DESC = """This is Nebix Bot Manager"""

setup(
    name="nebixbm",
    version="2.2.1",
    description="Nebix Bot Manager",
    long_description=LONG_DESC,
    long_description_content_type="text/plain",
    author="Nebix Team (Mohammad Salek)",
    url=" ",
    license="MIT",
    include_package_data=True,
    python_requires='>=3.8',
    packages=setuptools.find_packages(),
    entry_points={"console_scripts": ["nebixbm = nebixbm.__main__:main"]},
)
