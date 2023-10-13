# Variáveis
PYTHON = python3
SRC_DIR = src
MAIN_SCRIPT = main.py

# Comandos
run:
	$(PYTHON) $(SRC_DIR)/$(MAIN_SCRIPT)

install-dependencies:
	$(PYTHON) -m pip install -r requirements.txt

clean:
	rm -rf __pycache__

.PHONY: run install-dependencies clean
