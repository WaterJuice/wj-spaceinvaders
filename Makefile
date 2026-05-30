MODULE_NAME="wj_spaceinvaders"

# Default target: print usage message
.PHONY: help
help:
	@echo "Usage:"
	@echo "  make build        - Build project"
	@echo "  make clean        - Clean built package"
	@echo "  make check        - Format check and lint source"
	@echo "  make format       - Format source using Ruff"
	@echo "  make black        - Format source using Black (for long strings)"
	@echo "  make lint         - Lint source using pyright"
	@echo "  make publish      - Publish output/ to PyPI"
	@echo "  make dev          - Just create dev (.venv) setup"

# Version string from git tags (falls back to commit hash if no tags)
VERSION_STR=$(shell git describe --tags --always 2>/dev/null | sed 's/-/.post.dev/' | sed 's/-g/-/')

# Generate _version.py with the current version
.PHONY: version
version:
	@echo '__version__ = "$(VERSION_STR)"' > wj_spaceinvaders/_version.py

# Build the project
.PHONY: build
build: check-dependencies format-check lint version
	rm -rf output/
	uv build --out-dir output
	rm -f output/*.tar.gz

# Publish to PyPI
.PHONY: publish
publish: check-dependencies
	uv run wj-publish --pypi-only output/

# Clean build artefacts
.PHONY: clean
clean: check-dependencies
	rm -rf output/
	uv clean

# Check the format of code
.PHONY: check
check: format-check lint

# Check the format of code
.PHONY: format-check
format-check: check-dependencies
	uv run ruff format --check .
	uv run ruff check .

# Fix format of the code
.PHONY: format
format: check-dependencies
	uv run ruff format .
	uv run ruff check . --fix

# Fix format of the code
.PHONY: black
black: check-dependencies
	uv run black --preview --enable-unstable-feature string_processing .
	uv run ruff format .
	uv run ruff check . --fix

# Lint the code
.PHONY: lint
lint: check-dependencies
	uv run pyright

# Just create dev (.venv) setup
.PHONY: dev
dev: check-dependencies

# Check if uv is installed, install it if not
.PHONY: check-dependencies
check-dependencies: version
	uv --version 2>/dev/null && true || pip3 install uv
	uv sync
