import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="r53utils",
    version="0.2.1",
    author="Shumon Huque",
    author_email="shuque@gmail.com",
    description="Small module to work with Amazon Route53 DNS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shuque/r53utils",
    py_modules=['r53utils'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
