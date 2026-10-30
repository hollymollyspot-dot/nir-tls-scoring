.PHONY: build clean experiment

experiment:
	@echo " Запуск эксперимента..."
	python scripts/run_experiment.py

build: experiment
	@echo " Сборка сайта..."
	mkdocs build --strict

clean:
	rm -rf site/ docs/assets/ docs/includes/ data/results.csv data/.cache.json

serve: build
	mkdocs serve