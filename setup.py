"""
Setup script para Horas Trabalhadas - Timer Tool
"""

from setuptools import setup, find_packages
import os

# Lê o README para usar como descrição longa
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

setup(
    name="horas-trabalhadas",
    version="1.1.0",
    author="EDM Engenharia",
    description="Sistema para rastrear horas trabalhadas em diferentes projetos",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/edm-engenharia/horas-trabalhadas",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        # Tkinter já vem com Python, mas listamos aqui para documentação
    ],
    entry_points={
        "console_scripts": [
            "horas-trabalhadas=horas_trabalhadas.contador_horas:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)

