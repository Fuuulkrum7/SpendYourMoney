import numpy as np
import matplotlib.pyplot as plt
from keras import Sequential, models
from keras.layers import Dense, GRU
from keras.optimizers import RMSprop

from data_preparation import *
from info.file_loader import FileLoader


# Грузим все данные и предобрабатываем их
data_test = FileLoader.get_json("parsed_test_data.json")
data_main = FileLoader.get_json("parsed_data.json")

codes = FileLoader.get_json(".sector_codes.json")

# Нормализуем
test_his = normalize_data(data_test)[0]
sec_history = normalize_data(data_main)[0]

spliter = 1024 - 30 - 1

# Получаем данные для тренировки
train_data_h = sec_history[:]

# Делим по частям, часть на обучение
train_target = train_data_h[:, spliter:, :1]
train_data_h = train_data_h[:, spliter-120:spliter]

check_data_h = sec_history[1000:]

# Часть на постпроверку
check_target = check_data_h[:, spliter:, :1]
check_data_h = check_data_h[:, spliter-120:spliter]

# Часть на финальную проверку
test_target = test_his[:, spliter:, :1]
test_his = test_his[:, spliter-120:spliter]

graph = np.array(test_target)

# mark as growing or falling
test_target = np.array([is_growing(i) for i in test_target])

train_target = np.array([is_growing(i) for i in train_target])
check_target = np.array([is_growing(i) for i in check_target])

# model_test = models.load_model("model.keras")
# print(model_test.summary())
#
# test_loss, test_acc = model_test.evaluate(check_data_h, check_target)
# print('test_acc:', test_acc)
#
# a = model_test.predict(test_his)
#
# for i in range(len(a)):
#     plt.plot(list(range(1, len(graph[i]) + 1)), graph[i])
#     plt.title(f"{a[i]}, {test_target[i]}")
#     plt.show()
#     plt.clf()


# Создаем модель
model = Sequential()

# Добавляем слой для обработки последовательностей
# с 32 входными нейронами.
# Следующий слой тоже принимает последовательность
model.add(
    GRU(
        32,
        input_shape=train_data_h[0].shape,
        activation='relu',
        return_sequences=True
    )
)

# Принимает последовательность, содержит 64 нейрона
model.add(GRU(
    64,
    activation='relu'
))

# Принимает массив, возвращает массив из 3 элементов с вероятностью того или
# иного поведения акции. Содержит 3 нейрона
model.add(Dense(3, activation='sigmoid'))

# Компилируем сетку
model.compile(
    loss='mse',
    metrics=['mae'],
    optimizer=RMSprop()
)

# Начинаем обучение
history = model.fit(
    train_data_h,
    train_target,
    epochs=1000,
    batch_size=64,
    verbose=1,
)

# Проводим тестирование на данных для предпроверки
test_loss, test_acc = model.evaluate(check_data_h, check_target)
print('test_acc:', test_acc)

# Смотрим на график изменения точности при обучении
mae_history = history.history['mae']

plt.plot(range(1, len(mae_history) + 1), mae_history)
plt.xlabel('Epochs')
plt.ylabel('Validation MAE')
plt.show()
plt.clf()

# Сохраняем модель
model.save('model.keras')

# Делаем предсказание на тестовых данных
a = model.predict(test_his)

# Строим графики с предсказаниями сети и оценкой алгоритмической
for i in range(len(a)):
    plt.plot(list(range(1, len(graph[i]) + 1)), graph[i])
    plt.title(f"{a[i]}, {test_target[i]}")
    plt.show()
    plt.clf()
