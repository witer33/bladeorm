from setuptools import setup, find_packages


setup(
    name="bladeorm",
    version="0.0.5.3",
    license="MIT",
    author="Witer33",
    author_email="dev@witer33.com",
    packages=find_packages("src"),
    package_dir={"": "src"},
    url="https://github.com/witer33/bladeorm",
    keywords="postgres psql orm",
    install_requires=[
        "asyncpg",
    ],
)
