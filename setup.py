import os
import subprocess
from platform import system

from info.file_loader import FileLoader

os_is = "Unix"
settings = {}


def create_conda_venv():
    os.system("conda create -y -n invest")
    os.system("conda install -y -n invest pip")
    os.system(f"conda run -n invest pip{'3' if os_is == 'Unix' else ''} "
              f"install -r requirements.txt")


def create_python_venv():
    os.system("python -m venv venv2")
    if os_is == "Unix":
        part = "venv2/bin/python"
    else:
        part = r"venv2\Scripts\python"
    os.system(f"{part} -m pip install -r requirements.txt")


def create_user():
    sudo = "sudo -S" if os_is == "Unix" else ""
    result = "error"

    while "error" in result:
        root = input("Please, enter your MySQL root name: ")
        password = input("Input your MySQL password: ")

        a = f"""{sudo} mysql -u {root} -p{password} -e "CREATE USER IF NOT EXISTS 'TinkoffUser'@'localhost' 
                        IDENTIFIED BY '1nVestm$nt'; GRANT ALL PRIVILEGES ON *.* 
                         TO 'TinkoffUser'@'localhost';" """.replace("\n", "")
        try:
            result = subprocess.check_output(
                a, shell=True, text=True, encoding="utf-8"
            )
        except subprocess.CalledProcessError as e:
            print(e)
            print("Error occurred: login or password is incorrect")


def load_settings():
    global os_is, settings

    if system() == "Windows":
        os_is = system()

    settings = FileLoader.get_json("info/files/.current_settings.json")
    if settings is None or not ("venv" in settings):
        res = ""

        print("Hello! You need to choose conda or python.")
        while not (res in ['p', 'c']):
            res = input("Enter 'p' if you want to use python and 'c' "
                        "in case of conda\n")

        if settings is None:
            settings = FileLoader.get_json("info/files/.default_settings.json")
            if settings is None:
                print("Yoy deleted important file. Shit")
                quit(0)
        settings["venv"] = "python" if res == 'p' else "conda"
        create_user()

        create_conda_venv() if res == 'c' else create_python_venv()
        FileLoader.save_json("info/files/.current_settings.json", settings)
