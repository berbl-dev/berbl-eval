import pandas as pd

# These are Drugowitsch's results on these tasks (taken from his book).
drugowitsch_ga = pd.DataFrame({
    "generated_function": {
        "$\ln p(\MM \mid \DD)$": 118.81,
        "$K$": 2
    },
    "sparse_noisy_data": {
        "$\ln p(\MM \mid \DD)$": -159.07,
        "$K$": 2
    },
    "variable_noise": {
        "$\ln p(\MM \mid \DD)$": -63.12,
        "$K$": 2
    },
    "sine": {
        "$\ln p(\MM \mid \DD)$": -155.68,
        "$K$": 7
    },
})
drugowitsch_mcmc = pd.DataFrame({
    "generated_function": {
        "$\ln p(\MM \mid \DD)$": 174.50,
        "$K$": 3
    },
    "sparse_noisy_data": {
        "$\ln p(\MM \mid \DD)$": -158.55,
        "$K$": 2
    },
    "variable_noise": {
        "$\ln p(\MM \mid \DD)$": -58.59,
        "$K$": 2
    },
    "sine": {
        "$\ln p(\MM \mid \DD)$": -29.39,
        "$K$": 5
    },
})
