import os

import setup


setup.load_settings()

part = "conda activate invest"
if setup.settings["venv"] == "conda":
    if setup.os_is == "Unix":
        part = "source activate invest"
else:
    if setup.os_is == "Unix":
        part = "source venv2/bin/activate"
    else:
        part = r".\venv2\Scripts\activate"

os.system(f"{part} & python blade_runner.py")
