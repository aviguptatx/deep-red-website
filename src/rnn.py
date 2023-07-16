import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import numpy as np
from torch.autograd import Variable
import matplotlib.pyplot as plt
import gc
import sys
from rnn_parser import load_game, convert_plaintext_to_json


def get_pred_string(input: str):
    # Prints the entire numpy array
    np.set_printoptions(threshold=sys.maxsize)

    # Deterministic randomness
    torch.manual_seed(0)

    # Garbage collect
    gc.collect()

    # Enables device agnostic tensor creation
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Empty the CUDA cache
    with torch.no_grad():
        torch.cuda.empty_cache()
    torch.cuda.empty_cache()

    # Recurrent Neural Network (LSTM)
    class RNN(nn.Module):
        def __init__(self, n_inputs, n_hidden, X_in, seq_lengths):
            super(RNN, self).__init__()
            self.rnn = nn.LSTM(
                n_inputs, n_hidden, batch_first=True, num_layers=1, dropout=0.0
            )
            self.n_hidden = n_hidden
            self.X = X_in
            self.seq_lengths = seq_lengths
            self.FC = nn.Linear(self.n_hidden, 7)

        def forward(self):
            # Initialize the hidden state with all zeroes
            self.init_hidden()
            # Pack X
            self.X_packed = torch.nn.utils.rnn.pack_padded_sequence(
                Variable(self.X),
                self.seq_lengths,
                batch_first=True,
                enforce_sorted=False,
            )
            # Calculate values of hidden states
            _, self.hx = self.rnn(self.X_packed)
            # Run the states through the sigmoid function
            sigmoid = nn.Sigmoid()
            out = sigmoid(self.FC(self.hx[0][0])).to(device)

            return out

        def init_hidden(self):
            self.hx = Variable(torch.zeros(1, len(self.X), self.n_hidden).to(device))

    INPUT_LAYER_SIZE = 89
    HIDDEN_LAYER_SIZE = 17

    try:
        X = load_game(convert_plaintext_to_json(input))
    except:
        return []

    game_length = len(X[0])

    # Convert input to tensor
    X = torch.as_tensor(X, dtype=torch.float32).to(device)

    # Create model
    model = RNN(INPUT_LAYER_SIZE, HIDDEN_LAYER_SIZE, X, [game_length]).to(device)

    # Load the correct model parameters for the current game length
    parameter_file_name = "data/parameters/parameters-" + str(game_length) + ".pt"
    model.load_state_dict(torch.load(parameter_file_name, map_location=device))

    # Get and return prediction
    prediction = model()
    return prediction.detach().numpy().tolist()[0]
