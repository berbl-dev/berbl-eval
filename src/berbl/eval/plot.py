import os

import numpy as np

from . import get_data


def plot_training_data(ax, artifact_uri):
    """
    Plot training data (and denoised data for visual reference).
    """
    data = get_data(artifact_uri)
    ax.plot(data["X"], data["y"], "k+")
    ax.plot(data["X_denoised"], data["y_denoised"], "k--")


def plot_prediction(ax, artifact_uri):
    data = get_data(artifact_uri)

    # sort and get permutation of prediction data points
    X_test = data["X_test"].to_numpy().ravel()
    perm = np.argsort(X_test)
    X_test = X_test[perm]
    y_test = data["y_test"].to_numpy().ravel()[perm]

    # plot prediction means
    ax.plot(X_test, y_test, "C0")

    # plot prediction stds, if var exists in data
    try:
        var = data["var"].to_numpy().ravel()[perm]
        std = np.sqrt(var)
        ax.fill_between(X_test,
                        y_test - std,
                        y_test + std,
                        color="C0",
                        alpha=0.3)
        ax.plot(X_test, y_test - std, c="C0", linestyle="dotted")
        ax.plot(X_test, y_test + std, c="C0", linestyle="dotted")
    except KeyError:
        pass


def save_plot(eval_name, exp_name, plot_name, fig):
    fig_folder = f"eval/{eval_name}/plots/{exp_name}"
    os.makedirs(fig_folder, exist_ok=True)
    fig_file = f"{fig_folder}/{plot_name}.pdf"
    print(f"Storing plot in {fig_file}")
    fig.savefig(fig_file)
