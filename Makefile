all: tatsu pegen

pegen:
	poetry run python -mpegen src/ossify/phild.gram -o src/ossify/parser.py

tatsu:
	poetry run tatsu -o src/ossify/tparser.py src/ossify/tatsu.gram