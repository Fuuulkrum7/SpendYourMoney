import os
import subprocess
from platform import system

from info.file_loader import FileLoader


os_is = "Unix"


def create_conda_venv():
    os.system("conda create -n invest pip")

    run_conda()
    os.system("pip install -r requirements.txt")

def run_conda():
    path_conda = str(subprocess.check_output("conda info --base", shell=True,
                                         text=True))

    if os_is == "Unix":
        path_conda += "/etc/profile.d/conda.sh"
        path_conda = path_conda.replace('\n', '')
        os.system(f"source {path_conda}")
    else:
        os.system(f".{path_conda}\\bin\\activate")

    if os_is == "Unix":
        os.system("source activate invest")
    else:
        os.system("conda activate invest")

def create_python_venv():
    os.system("python -m venv venv2")
    run_python()
    os.system("pip install -r requirements.txt")

def run_python():
    if os_is == "Unix":
        os.system("source venv2/bin/activate")
    else:
        os.system(r".\venv\Scripts\activate")

def create_user():
    root = input("Please, enter your MySQL root name\n")
    # password = input("Please, enter your MySQL root password")
    result = "ERROR 1045".lower()

    while "error" in result:
        if os_is == "Unix":
            print("First required password is for sudo user. "
                  "Second is for root user of MySQL")
        else:
            print("Required password is for root user of MySQL")
        try:
            if os_is == "Unix":
                result = subprocess.check_output(
                    f"""sudo -S mysql -u {root} -p -e "CREATE USER IF NOT 
                    EXISTS 'TinkoffUser'@'localhost' IDENTIFIED 
                    BY '1nVestm$nt'; GRANT ALL PRIVILEGES ON *.* 
                    TO 'TinkoffUser'@'localhost';" """, shell=True, text=True,
                    encoding="utf-8"
                )
            else:
                result = subprocess.check_output(
                    f"""mysql -u {root} -p -e mysql -u {root} -p 
                    -e "CREATE USER IF NOT EXISTS 'TinkoffUser'@'localhost' 
                    IDENTIFIED BY '1nVestm$nt'; GRANT ALL PRIVILEGES ON *.* 
                    TO 'TinkoffUser'@'localhost';" """,
                    shell=True, text=True, encoding="utf-8"
                )
        except subprocess.CalledProcessError:
            if "error 1045" in result.lower():
                print("Error occurred: login or password is incorrect")
                root = input("Please, enter your MySQL root name\n")
            else:
                print(result)

def load_settings():
    global os_is

    if system() == "Windows":
        os_is = system()

    settings = FileLoader.get_json("info/files/.current_settings.json")
    if not ("venv" in settings):
        res = ""

        print("Hello! You need to choose conda or python.")
        while not (res in ['p', 'c']):
            res = input("Enter 'p' if you want to use python and 'c' "
                        "in case of conda\n")
        settings["venv"] = "python" if res == 'p' else "conda"
        FileLoader.save_json("info/files/.current_settings.json", settings)
        create_user()

        create_conda_venv() if res == 'c' else create_python_venv()

    if settings["venv"] == "conda":
        try:
            run_conda()
        except Exception as e:
            print("execution omg", e)
            create_conda_venv()
    else:
        try:
            run_python()
        except Exception as e:
            print(e)
            create_python_venv()
