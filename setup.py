import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="autohelper",
    version="0.0.5",
    author="CTO",
    author_email="firedcto@gmail.com",
    description="Automation with Computer Vision for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CrashTechnologyOfficer/autoui",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
    install_requires=[
        'adbutils==2.2.1',
        'numpy~=1.26.4',
        'PyDirectInput~=1.0.4',
        'pywin32==306',
        'typing-extensions~=4.10.0',
        'PySide6~=6.6.2',
        'paddlepaddle~=2.6.0',
        'paddleocr~=2.7.0.3',
    ],
    python_requires='>=3.4',
)
