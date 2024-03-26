from sklearn.linear_model import RidgeCV, Ridge
import numpy as np

class NeuronOutput:

    model: Ridge = None,
    fitted_model: Ridge = None,
    reservoir_output: np.ndarray = None,
    reservoir_input: np.ndarray = None,
    model_params: dict = None,
    score: float = None,
    CV: bool = False

    def __init__(self,
                 reservoir_output: np.ndarray,
                 reservoir_input: np.ndarray,
                 CV: bool = False
                 ):

        self.initialise_model(reservoir_output, reservoir_input, CV)
        self.train_model()
    def initialise_model(self,reservoir_output,reservoir_input, CV) -> None:

        self.reservoir_output = reservoir_output
        self.reservoir_input = reservoir_input
        self.CV = CV

        if CV:
            self.model = RidgeCV(alpha_per_target=True,alphas=[0.001,0.01,0.1,1,10,100,1000],store_cv_values=False,cv=None)
        else:
            self.model = Ridge()

    def train_model(self) -> None:
        self.fitted_model = self.model.fit(self.reservoir_output,self.reservoir_input)
        self.model_params = self.fitted_model.get_params()
        self.score = self.fitted_model.score(self.reservoir_output,self.reservoir_input)



