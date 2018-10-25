"""
Created on 08.11.2017

@author: rmueller
"""
from keras.layers import Dense

from model.IPredictor import IPredictor

from model.StockData import StockData
from utils import load_keras_sequential, save_keras_sequential, read_stock_market_data
from model.CompanyEnum import CompanyEnum
from logger import logger
from matplotlib import pyplot as plt
from keras.models import Sequential
from definitions import PERIOD_1, PERIOD_2
from keras.callbacks import History
import numpy as np

TEAM_NAME = "team_blue"

RELATIVE_PATH = 'predicting/predictor/' + TEAM_NAME + '/' + TEAM_NAME + '_predictor_data'
MODEL_FILE_NAME_STOCK_A = TEAM_NAME + '_predictor_stock_a_network'
MODEL_FILE_NAME_STOCK_B = TEAM_NAME + '_predictor_stock_b_network'

# Neural network configuration -> TODO see Keras Documentation
INPUT_SIZE = 42  # TODO


class TeamBlueBasePredictor(IPredictor):
    """
    Predictor based on an already trained neural network.
    """

    def __init__(self, nn_filename: str):
        """
        Constructor: Load the trained and stored neural network.

        Args:
            nn_filename: The filename to load the trained data from
        """
        # Try loading a stored trained neural network...
        self.model = load_keras_sequential(RELATIVE_PATH, nn_filename)
        assert self.model is not None

        # TODO compile loaded model

    def doPredict(self, data: StockData) -> float:
        """
        Use the loaded trained neural network to predict the next stock value.
    
        Args:
          data: historical stock values of a company

        Returns:
          predicted next stock value for that company
        """
        #self.model.compile(loss='mean_squared_error', optimizer='sgd')
        tmp_data = data.get_from_offset(data.get_row_count() - 5)
        tmp = np.array([[tmp_data[0][1], tmp_data[1][1], tmp_data[2][1], tmp_data[3][1], tmp_data[4][1]]])


        pred = self.model.predict(tmp)


        res = data.get_last()[1];

        if (pred <= 0.5):
            res = res * 0.9;
        else:
            res = res * 1.1


        # TODO: extract needed data for neural network and predict result
        return res


class TeamBlueStockAPredictor(TeamBlueBasePredictor):
    """
    Predictor for stock A based on an already trained neural network.
    """

    def __init__(self):
        """
        Constructor: Load the trained and stored neural network.
        """
        super().__init__(MODEL_FILE_NAME_STOCK_A)


class TeamBlueStockBPredictor(TeamBlueBasePredictor):
    """
    Predictor for stock B based on an already trained neural network.
    """

    def __init__(self):
        """
        Constructor: Load the trained and stored neural network.
        """
        super().__init__(MODEL_FILE_NAME_STOCK_B)


###############################################################################
# The following code trains and stores the corresponding neural network
###############################################################################


def learn_nn_and_save(training_data: StockData, test_data: StockData, filename_to_save: str):
    network = create_model()

    # TODO: learn network and draw results

    #np.append([[1, 2, 3], [4, 5, 6]], [7, 8, 9], axis=0)

    x_train = np.array([]);
    y_train = np.array([]);

    i = 0
    batch = 5
    while i < training_data.get_row_count()-batch:
        tmp = np.array([]);
        for j in range(0, batch):
            i = i + 1;
            diff = training_data.get(i)[1] - training_data.get(i + 1)[1]
            tmp = np.insert(tmp, j, diff)

        diff_y = 0;
        if (i < training_data.get_row_count() - 1):
            diff_y = training_data.get(i - 1)[1] - training_data.get(i)[1]

        if (diff_y > 0):
            y_train = np.append(y_train, 1)
        else:
            y_train = np.append(y_train, 0)

        x_train = np.append(x_train, tmp, axis=0);

    x_train = x_train.reshape((int(x_train.shape[0]/5),5));
    y_train = y_train.reshape((-1, 1));

    #for i in range(0, training_data.get_row_count() - 1):
    #    diff = training_data.get(i)[1] - training_data.get(i + 1)[1]

    #    if (diff < 0):
    #        y_train.append([1])
    #    else:
    #        y_train.append([0])


    network.compile(loss='mean_squared_error', optimizer='sgd')
    network.fit(x_train, y_train , epochs=10, batch_size=5)

    # Save trained model: separate network structure (stored as JSON) and trained weights (stored as HDF5)
    save_keras_sequential(network, RELATIVE_PATH, filename_to_save)


def create_model() -> Sequential:
    network = Sequential()

    # TODO: build model

    network.add(Dense(5, input_dim=5, activation='relu'))
    #network.add(Dense(5, activation='relu'))
    network.add(Dense(1, activation='sigmoid'))
    network.compile(loss='mean_squared_error', optimizer='sgd')


    return network


def draw_history(history: History):
    plt.figure()
    plt.plot(history.history['loss'])
    plt.title('training loss / testing loss by epoch')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['training', 'testing'], loc='best')


def draw_prediction(dates: list, awaited_results: list, prediction_results: list):
    plt.figure()

    plt.plot(dates[INPUT_SIZE:], awaited_results, color="black")  # current prices in reality
    plt.plot(dates[INPUT_SIZE:], prediction_results, color="green")  # predicted prices by neural network
    plt.title('current prices / predicted prices by date')
    plt.ylabel('price')
    plt.xlabel('date')
    plt.legend(['current', 'predicted'], loc='best')

    plt.show()


if __name__ == "__main__":
    logger.debug("Data loading...")
    training_stock_market_data = read_stock_market_data([CompanyEnum.COMPANY_A, CompanyEnum.COMPANY_B], [PERIOD_1])
    test_stock_market_data = read_stock_market_data([CompanyEnum.COMPANY_A, CompanyEnum.COMPANY_B], [PERIOD_2])

    company_a_training_stock_data: StockData = training_stock_market_data[CompanyEnum.COMPANY_A]
    company_a_test_stock_data: StockData = test_stock_market_data[CompanyEnum.COMPANY_A]

    logger.debug(f"Data for Stock A loaded")
    learn_nn_and_save(company_a_training_stock_data, company_a_test_stock_data, MODEL_FILE_NAME_STOCK_A)

    company_b_training_stock_data: StockData = training_stock_market_data[CompanyEnum.COMPANY_B]
    company_b_test_stock_data: StockData = test_stock_market_data[CompanyEnum.COMPANY_B]

    logger.debug(f"Data for Stock B loaded")
    learn_nn_and_save(company_b_training_stock_data, company_b_test_stock_data, MODEL_FILE_NAME_STOCK_B)
