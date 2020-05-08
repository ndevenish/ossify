all:
	poetry run python -mpegen src/ossify/phild.gram -o src/ossify/parser.py
opt:
	poetry run python -mpegen src/ossify/phild.gram -o src/ossify/parser.py --optimized
