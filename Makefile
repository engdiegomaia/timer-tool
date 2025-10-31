.PHONY: help install install-dev run test clean build dist

help:
	@echo "Comandos disponíveis:"
	@echo "  make install      - Instala o pacote no ambiente atual"
	@echo "  make install-dev  - Instala o pacote em modo desenvolvimento"
	@echo "  make run          - Executa a aplicação"
	@echo "  make clean        - Remove arquivos temporários e builds"
	@echo "  make build        - Cria o pacote distribuível"
	@echo "  make dist         - Cria distribuições (wheel e source)"

install:
	pip install .

install-dev:
	pip install -e .

run:
	python -m horas_trabalhadas.contador_horas

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf __pycache__
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete

build:
	python setup.py sdist bdist_wheel

dist: clean build
	@echo "Distribuições criadas em dist/"

