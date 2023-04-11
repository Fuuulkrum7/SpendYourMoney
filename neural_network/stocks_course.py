import numpy as np
import matplotlib.pyplot as plt
from keras import Sequential, models
from keras.layers import Dense, GRU
from keras.optimizers import RMSprop

from data_preparation import *


data_test = get_json("parsed_test_data.json")
data_main = get_json("parsed_data.json")

codes = get_json(".sector_codes.json")

test_his = normalize_data(data_test)[0]
sec_history = normalize_data(data_main)[0]

spliter = 1024 - 30 - 1

train_data_h = sec_history[:]

train_target = train_data_h[:, spliter:, :1]
train_data_h = train_data_h[:, spliter-120:spliter]

check_data_h = sec_history[1000:]

check_target = check_data_h[:, spliter:, :1]
check_data_h = check_data_h[:, spliter-120:spliter]

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


model = Sequential()

model.add(
    GRU(
        32,
        input_shape=train_data_h[0].shape,
        activation='relu',
        return_sequences=True
    )
)

model.add(GRU(
    64,
    activation='relu'
))

model.add(Dense(3, activation='sigmoid'))

model.compile(
    loss='mse',
    metrics=['mae'],
    optimizer=RMSprop()
)

history = model.fit(
    train_data_h,
    train_target,
    epochs=1000,
    batch_size=64,
    verbose=1,
)

test_loss, test_acc = model.evaluate(check_data_h, check_target)
print('test_acc:', test_acc)

mae_history = history.history['mae']

plt.plot(range(1, len(mae_history) + 1), mae_history)
plt.xlabel('Epochs')
plt.ylabel('Validation MAE')
plt.show()
plt.clf()

model.save('model.keras')

a = model.predict(test_his)

for i in range(len(a)):
    plt.plot(list(range(1, len(graph[i]) + 1)), graph[i])
    plt.title(f"{a[i]}, {test_target[i]}")
    plt.show()
    plt.clf()
