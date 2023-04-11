import json
import math
from datetime import datetime
import numpy as np


def norm_word(word) -> int:
    parsed = 0
    for i in range(len(word)):
        parsed += ord(word[i]) * 10 ** (len(word) - 1 - i)

    return parsed


def normalize_data(data) -> np.array:
    codes = get_json("sector_codes.json")
    securities_history = []
    coefs = []

    for key, value in data.items():
        # А это чтобы лотность уменьшить чутка
        parsed = [1 / value["lot"]]

        alpha_parsed = norm_word(value["currency"])
        parsed.append(alpha_parsed / 100000)

        # По индексу меняем сектор
        alpha_parsed = value["sector"]
        if not alpha_parsed:
            alpha_parsed = "nothing"

        # Пока секторов у нас меньше 30, так что все ок
        alpha_parsed = codes[alpha_parsed] / 20
        parsed.append(alpha_parsed)

        # Получаем текст, с помощью кода буков парсим в числа
        alpha_parsed = norm_word(value["country_code"])
        parsed.append(alpha_parsed / 1000)

        parsed.append(value["stock_type"] / 8)

        # Так как при делении значения капец мелкие, делаем вот так))
        parsed.append(math.log(value["issue_size"], 12960541337338))

        parsed.append(value["otc_flag"])
        parsed.append(value["div_yield_flag"])

        # Нормализация даты ipo. До 1900 явно ничего не было в данных,
        # а 2100 год ещё далеко
        parsed.append((int(value["ipo_date"][:4]) - 1900) / 200)

        sub_history = value.pop("history")
        value.pop("security_name")

        price, volume, days, months, day_of_week, sec = [], [], [], [], [], []

        for i in sub_history:
            date_ = datetime.strptime(i["info_time"][:10], '%Y-%m-%d')
            price.append(i["price"])
            volume.append(float(i["volume"]))
            days.append(float(date_.day))
            months.append(float(date_.month))
            day_of_week.append(float(date_.weekday()))
            sec.append(parsed)

        price, volume, days, months, day_of_week = np.array(price), \
            np.array(volume), np.array(days), \
            np.array(months), np.array(day_of_week)

        delta = 1024 - len(sub_history)
        # Нормализуем данные
        coefs.append(np.sqrt(np.sum(price ** 2)))

        price /= np.sqrt(np.sum(price**2))
        price = np.concatenate([np.zeros((delta,)), price])

        volume /= np.sqrt(np.sum(volume**2))
        volume = np.concatenate([np.zeros((delta,)), volume])

        days /= 31
        days = np.concatenate([np.zeros((delta,)), days])

        months /= 12
        months = np.concatenate([np.zeros((delta,)), months])

        day_of_week /= 7
        day_of_week = np.concatenate([np.zeros((delta,)), day_of_week])

        securities_history.append(np.stack(
            [price, volume, days, months, day_of_week], axis=-1
        ))

        sec = np.concatenate([np.zeros((delta, 9)), np.array(sec)])

        securities_history[-1] = np.concatenate(
            [
                securities_history[-1],
                sec
            ],
            axis=1
        )

    return [np.array(securities_history), np.array(coefs)]


def is_growing(seq) -> np.array:
    max_d = []
    min_d = []
    deltas = []

    prev_0 = 0

    for i in range(len(seq) - 1):
        deltas.append(seq[i + 1][0] - seq[i][0])
        prev_1 = prev_0
        prev_0 = seq[i][0]
        curr = seq[i + 1][0]

        if prev_1 < prev_0 and prev_0 > curr:
            max_d.append(prev_0)

        elif prev_1 > prev_0 and prev_0 < curr:
            min_d.append(prev_0)

    deltas = np.array(deltas)
    min_d = np.array(min_d)
    max_d = np.array(max_d)

    avg = np.average(deltas)
    avg_high = max_d[-1] - max_d[1]
    avg_low = min_d[-1] - min_d[1]
    delta = (seq[-1][0] - seq[0][0]) / seq[0][0]

    d_av = (np.average(seq[-3:]) - np.average(seq[0:3])) / seq[0][0]

    # print(avg, delta, avg_low, avg_high, d_av)

    if abs(avg) <= 0.002:
        avg = 0.5
    elif avg < 0:
        avg = 0
    else:
        avg = 1

    if delta < -0.05:
        delta = 0
    elif delta > 0.05:
        delta = 1
    else:
        delta = 0.5

    if d_av < -0.05:
        d_av = 0
    elif d_av > 0.05:
        d_av = 1
    else:
        d_av = 0.5

    if abs(avg_high) < 0.02:
        avg_high = 0.5
    elif avg_high < 0:
        avg_high = 0
    else:
        avg_high = 1

    if abs(avg_low) < 0.02:
        avg_low = 0.5
    elif avg_low < 0:
        avg_low = 0
    else:
        avg_low = 1

    # print(avg, delta, avg_low, avg_high, d_av)

    coef = delta * 0.35 + d_av * 0.25 + avg * 0.2 + \
        avg_high * 0.1 + avg_low * 0.1

    # plt.plot(list(range(1, len(seq) + 1)), seq)
    # plt.title(f"{coef}")
    # plt.show()
    # plt.clf()

    if coef >= 0.6:
        return np.array([0, 0, 1])

    if coef < 0.4:
        return np.array([1, 0, 0])
    return np.array([0, 1, 0])


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
