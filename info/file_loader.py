import json
from typing import Sized


class FileLoader:
    @staticmethod
    def get_file(file_name: str) -> list[Sized] | None:
        try:
            file = open(file_name)
            res = file.read().splitlines()
            res = list(filter(len, res))
            file.flush()
        except FileNotFoundError:
            res = None

        return res

    @staticmethod
    def get_json(file_name: str) -> dict | None:
        try:
            file = open(file_name)
            res = json.load(file)
            file.flush()
        except FileNotFoundError:
            res = None
        except ValueError:
            res = None

        return res

    @staticmethod
    def save_file(file_name: str, data: list[object]) -> bool:
        try:
            file = open(file_name, "w")
            for i in data:
                file.write(str(i) + "\n")

            file.flush()
            return True
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def save_json(file_name: str, data: dict) -> bool:
        try:
            json.dump(
                json.dumps(data),
                open(file_name, "w")
            )

            return True
        except Exception as e:
            print(e)
            return False
