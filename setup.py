from setuptools import setup, find_packages

setup(
    name="chatgpt_auto",
    version="0.1",  
    packages=find_packages(),  
    install_requires=[],
    author="Neo",  
    author_email="neonabukodonosor@gmail.com",  
    description="Interact with chatgpt using Selenium",
    long_description=open("README.md").read(),  
    long_description_content_type="text/markdown",  
    url="https://github.com/neonabuko/chatgpt_auto.git",  
    classifiers=[  
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  
        "Operating System :: OS Independent",
    ],
)
