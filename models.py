from copy import deepcopy
from random import randint
from time import time

# !pip install beautifultable
from beautifultable import BeautifulTable, STYLE_BOX
from tensorflow.keras.backend import clear_session
from tensorflow.python.keras.layers import Dense, Embedding, Flatten, SimpleRNN, Dropout, LSTM, Bidirectional
from tensorflow.python.keras.models import Sequential
from termcolor import cprint, colored

from data_making import main_fun, make_data
from func import metrics, show


def human_time(time_val):
    return "{}:{}".format(int(time_val // 60 % 60), round(time_val % 60, 2))


def run_models(from_main_fun, epochs, adding=""):
    scores = {}

    def run_one_model(model, x_train, x_test, epc, name="model"):
        name += adding
        cprint(name, "green")
        start_time = time()
        sc_epc = show(model, x_train, x_test, y_train, y_test, plt=True, eps=epc, plt_title=name)
        scores[name] = [sc_epc, time() - start_time]
        clear_session()

    def find_best_for_sequential(x_train, x_test):
        print(end="\n\n")
        max_score = 0
        best = [0, 0]
        for k in range(1):
            model = Sequential()
            num = randint(100, 250)
            num2 = randint(20, num - 20)
            model.add(Dense(num, activation="relu", input_dim=dict_len + 1))
            model.add(Dense(num2, activation="relu"))
            model.add(Dense(1, activation='sigmoid'))
            model.compile(optimizer="sgd", loss='binary_crossentropy', metrics=metrics)
            for _ in range(2):
                model.fit(x_train, y_train, epochs=5, batch_size=200, validation_split=0.1, verbose=0)
                srs = model.evaluate(x_test, y_test, verbose=0)
                if max_score < srs[3]:
                    max_score = srs[3]
                    best = [num, num2]

            clear_session()
        print("Max:", max_score)
        print("Best:", best)
        return best

    def sequential(best):
        model = Sequential()
        model.add(Dense(best[0], activation="relu", input_dim=dict_len + 1))
        model.add(Dense(best[1], activation="relu"))
        model.add(Dense(1, activation='sigmoid'))
        model.compile(optimizer="sgd", loss='binary_crossentropy', metrics=metrics)
        return model

    def embedding():
        model = Sequential()
        model.add(Embedding(dict_len + 1, 32, input_length=pad_len))
        model.add(Flatten())
        model.add(Dense(30, activation="sigmoid"))
        model.add(Dense(1, activation='sigmoid'))
        model.compile(optimizer="adam", loss='binary_crossentropy', metrics=metrics)
        return model

    def simple_rnn():
        model = Sequential()
        model.add(Embedding(dict_len + 1, 32, input_length=pad_len))
        model.add(SimpleRNN(10))
        model.add(Dropout(0.1))
        model.add(Dense(1, activation='sigmoid'))
        model.compile(optimizer="adam", loss='binary_crossentropy', metrics=metrics)
        return model

    def double_lstm():
        model = Sequential()
        model.add(Embedding(dict_len + 1, 32, input_length=pad_len))
        model.add(LSTM(10, return_sequences=True))
        model.add(LSTM(10))
        model.add(Dropout(0.6))
        model.add(Dense(1, activation='sigmoid'))
        model.compile(optimizer="adam", loss='binary_crossentropy', metrics=metrics)
        return model

    def bidirectional_lstm():
        model = Sequential()
        model.add(Embedding(dict_len + 1, 32, input_length=pad_len))
        model.add(Bidirectional(LSTM(10)))
        model.add(Dropout(0.6))
        model.add(Dense(1, activation='sigmoid'))
        model.compile(optimizer="adam", loss='binary_crossentropy', metrics=metrics)
        return model

    def lstm():
        model = Sequential()
        model.add(Embedding(dict_len + 1, 32, input_length=pad_len))
        model.add(LSTM(10))
        model.add(Dropout(0.6))
        model.add(Dense(1, activation='sigmoid'))
        model.compile(optimizer="adam", loss='binary_crossentropy', metrics=metrics)
        return model

    x_train_pre, x_test_pre, x_train_vec, x_test_vec, x_train_vec_td_idf, x_test_vec_td_idf, y_test, y_train, dict_len, pad_len = from_main_fun

    bst = find_best_for_sequential(x_train_vec, x_test_vec)
    clear_session()

    run_one_model(sequential(bst), x_train_vec, x_test_vec, epc=epochs[0], name="Sequential")
    run_one_model(embedding(), x_train_pre, x_test_pre, epc=epochs[1], name="Embedding")
    run_one_model(simple_rnn(), x_train_pre, x_test_pre, epc=epochs[2], name="Simple RNN")
    run_one_model(double_lstm(), x_train_pre, x_test_pre, epc=epochs[3], name="Double LSTM")
    run_one_model(bidirectional_lstm(), x_train_pre, x_test_pre, epc=epochs[4], name="Bidirectional LSTM")
    run_one_model(lstm(), x_train_pre, x_test_pre, epc=epochs[5], name="Simple LSTM")

    cprint("End of modeling", "cyan")
    print(end="\n\n")
    return scores


data = make_data(data_len=500)
ig_scores = run_models(main_fun(
    deepcopy(data),
    rem_stop_words=True,
    is_ig=True,
    num_of_wds=500
    # pad_len=500
), adding=" with 2000 words", epochs=[50, 4, 4, 4, 4, 4])

simple_scores = run_models(main_fun(
    data,
    rem_stop_words=True,
    is_ig=True,
    num_of_wds=500
    # pad_len=500
), adding=" with 4000 words", epochs=[50, 4, 4, 4, 4, 4])


table = BeautifulTable()
table.column_headers = ["name", "loss", "Precision", "Recall", "F1 score", "Accuracy", "time", "epoch"]
for i, j in zip(ig_scores, simple_scores):
    s = ig_scores[i][0][0]
    f1_score = 2 * s[1] * s[2] / (s[1] + s[2]) if s[1] + s[2] != 0 else 0
    table.append_row(
        [i, s[0], s[1], s[2], f1_score, s[3], human_time(ig_scores[i][1]), ig_scores[i][0][1]])
    s = simple_scores[j][0][0]
    f1_score = 2 * s[1] * s[2] / (s[1] + s[2]) if s[1] + s[2] != 0 else 0
    table.append_row([j, s[0], s[1], s[2], f1_score, s[3], human_time(simple_scores[j][1]),
                      simple_scores[j][0][1]])
print(table, end="\n\n\n")
cprint('MAX Accuracy table', 'green')
table = BeautifulTable()
table.set_style(STYLE_BOX)

lis = ["name", "loss", "Precision", "Recall", "F1 score", "Accuracy", "time", "epoch"]
table.column_headers = [colored(i, "red") for i in lis]
for i, j in zip(ig_scores, simple_scores):
    s = ig_scores[i][0][2]
    f1_score = 2 * s[1] * s[2] / (s[1] + s[2]) if s[1] + s[2] != 0 else 0
    table.append_row(
        [i, s[0], s[1], s[2], f1_score, s[3], human_time(ig_scores[i][1]), ig_scores[i][0][3]])
    s = simple_scores[j][0][2]
    f1_score = 2 * s[1] * s[2] / (s[1] + s[2]) if s[1] + s[2] != 0 else 0
    table.append_row([j, s[0], s[1], s[2], f1_score, s[3], human_time(simple_scores[j][1]),
                      simple_scores[j][0][3]])

print(table)