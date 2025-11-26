from setuptools import setup, find_packages

setup(
    name="auxiliar-lattes",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        pkg.strip() for pkg in open("requirements.txt").readlines()
    ],
    author="Seu Nome",
    description="Descrição do projeto",
    python_requires=">=3.10",
)
