import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="code_20201021_jagratiasati",  # Replace with your own username
    version="0.0.1",
    author="Jagrati Asati",
    author_email="asati.jagrati93@gmail.com",
    description="Body Mass Index Calculator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    include_package_data=True,
    entry_points={"console_scripts": ["calculator = calculator.main:main"]},
    python_requires=">=3.6",
    install_requires=[
        "pandas>=1.0.0",
        "pytest",
    ],
    extra_require={
        "dev": [
            "pytest=6.1.1",
        ]
    },
)
