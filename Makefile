PYTHON = python3
MAIN = pac-man.py
CONFIG = config.json
NAME = PacMan

.PHONY: run install debug clean lint spec package zip fclean re

run:
	@uv run $(PYTHON) $(MAIN) $(CONFIG)

install:
	uv sync

debug:
	uv run $(PYTHON) -m pdb $(MAIN) $(CONFIG)

clean:
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type d -name ".mypy_cache" -exec rm -rf {} +
	@find . -type d -name ".pytest_cache" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete

lint:
	@flake8 .
	@mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

spec:
	uv run pyinstaller --clean --noconfirm --onedir --name $(NAME) --add-data "assets:assets" --add-data "$(CONFIG):." --collect-all mazegenerator $(MAIN)

package:
	uv run pyinstaller --clean --noconfirm $(NAME).spec
	cp PACKAGE_README.txt dist/$(NAME)/README.txt

zip: package
	rm -f dist/$(NAME)-linux.zip
	cd dist && zip -r $(NAME)-linux.zip $(NAME)

fclean:
	rm -rf build dist

re: fclean package