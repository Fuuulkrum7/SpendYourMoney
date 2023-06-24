import subprocess

import setup
from info.file_loader import FileLoader

done = False

while not done:
    setup.load_settings()

    part = "conda run -n invest python"
    if setup.settings["venv"] == "python":
        if setup.os_is == "Unix":
            part = "venv2/bin/python"
        else:
            part = r"venv2\Scripts\python"

    try:
        result = subprocess.check_output(
            f"{part} blade_runner.py",
            shell=True, text=True, encoding="utf-8"
        )
        done = not len(result)
    except Exception as e:
        print(e)
        print("fixing...")
        setup.settings.pop("venv")

        FileLoader.save_json("info/files/.current_settings.json",
                             setup.settings)
