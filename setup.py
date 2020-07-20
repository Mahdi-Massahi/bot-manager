from setuptools import setup


LONG_DESC = "Nebix Trading Bot"

setup(
    name="nebixbot",
    version="0.1.0",
    description="Nebix Trading Bot",
    long_description=LONG_DESC,
    long_description_content_type="text/plain",
    author="Nebix Team (Mohammad Salek)",
    url=" ",
    license="MIT",
    include_package_data=True,
    packages=["nebixbot", ],
    entry_points={"console_scripts": ["nebixbot = nebixbot.__main__:main"]},
)
