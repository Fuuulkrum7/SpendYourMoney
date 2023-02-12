def installation(modules: list) -> None:
    """Вызывает pip install для модулей"""
    import sys, subprocess
    for module in modules:
        subprocess.check_call([sys.executable, "-m", "pip", "install", module])
