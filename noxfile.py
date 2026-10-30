import nox

@nox.session
def experiment(session):
    """Запуск эксперимента: генерация графиков и таблиц"""
    session.install("-r", "requirements.txt")
    session.run("python", "scripts/run_experiment.py")

@nox.session
def build(session):
    """Сборка сайта: эксперимент + mkdocs"""
    session.install("-r", "requirements.txt")
    session.run("python", "scripts/run_experiment.py")
    session.run("mkdocs", "build", "--strict")

@nox.session
def serve(session):
    """Локальный предпросмотр сайта"""
    session.install("-r", "requirements.txt")
    session.run("python", "scripts/run_experiment.py")
    session.run("mkdocs", "serve")

@nox.session
def clean(session):
    """Очистка артефактов сборки"""
    import shutil
    import os
    for path in ["site", "docs/assets", "docs/includes"]:
        if os.path.exists(path):
            shutil.rmtree(path)
    for path in ["data/results.csv", "data/.cache.json"]:
        if os.path.exists(path):
            os.remove(path)