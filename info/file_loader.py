import json
from typing import Sized


class FileLoader:
    @staticmethod
    def get_file(file_name: str, datatype=list) -> list[Sized] or str or None:
        try:
            file = open(file_name)
            res = file.read()
            if datatype == list:
                res = res.splitlines()
                res = list(filter(len, res))

            file.close()
        except FileNotFoundError:
            res = None

        return res

    @staticmethod
    def get_json(file_name: str) -> dict or None:
        try:
            file = open(file_name)
            res = json.load(file)
            file.close()
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

            file.close()
            return True
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def save_json(file_name: str, data: dict) -> bool:
        try:
            f = open(file_name, "w")
            json.dump(
                json.dumps(data),
                f
            )
            f.close()

            return True
        except Exception as e:
            print(e)
            return False
