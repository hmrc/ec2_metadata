from setuptools import setup

setup(
    name="mdtp-ec2-metadata",
    version="0.1.0",
    py_modules=["ec2_metadata"],
    entry_points={
        "console_scripts": [
            "ec2-metadata=ec2_metadata:main",
            "instance-identity=ec2_metadata:main",
        ]
    },
    install_requires=["requests"],
)
