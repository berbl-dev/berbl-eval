import warnings

import click
import matplotlib.pyplot as plt
import numpy as np
from berbl.eval import *
from berbl.eval.plot import *
from berbl.eval.drugowitsch import *

warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)

# TODO Store via PGF backend with nicer LaTeXy fonts etc.
# https://jwalton.info/Matplotlib-latex-PGF/

import matplotlib
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42

pd.options.display.max_rows = 2000

# Metric and whether higher is better.
metrics = {"p_M_D": True, "mae": False, "size": False}
ropes = {"p_M_D": 10, "mae": 0.01, "size": 0.5}

reps = 10

# Not entirely sure whether this generalizes properly but it seems to work so
# far.
def fix_artifact_uri(uri, path):
    path = path.removesuffix("/")
    dir = path.split("/")[-1]
    uri = uri.split(dir)[-1]
    return f"{path}/{uri}"


def table_compare_drugowitsch(runs):
    print()
    print("# Comparison with Drugowitsch's results (ln p(M | D) and size)")
    print()

    runs = keep_unstandardized(runs)

    print("Keeping only reproduction BERBL experiments …")
    # First level of index is algorithm.
    rs = runs.loc["berbl"]
    # Second level of index is variant.
    rs = rs.loc[["book", "non_literal"]]

    assert len(rs) == reps * 5 * (4 + 4)

    rs = rs.rename(lambda s: s.removeprefix("metrics.elitist."), axis=1)

    print("Checking literal and modular backends for being equal …")

    books = rs.loc["book"]
    books = books.set_index(["params.data.seed", "params.seed"], append=True)
    books = books.reset_index(level=1, drop=True)
    books = books.sort_index()
    non_literals = rs.loc["non_literal"]
    non_literals = non_literals.set_index(["params.data.seed", "params.seed"],
                                          append=True)
    non_literals = non_literals.reset_index(level=1, drop=True)
    non_literals = non_literals.sort_index()

    print(f"Comparing {len(books)} literal with {len(non_literals)} runs.")
    mae = np.abs(non_literals.p_M_D - books.p_M_D).sum() / len(books)
    frac_neq = (books.p_M_D != non_literals.p_M_D).sum() / len(books)
    print(f"ln p(M | D) MAE of literal and modular backends is {mae}.")
    print(
        f"Fraction of not-exactly-equal ln p(M | D) results of literal and modular backends is {frac_neq}."
    )
    frac_neq_higher = (books.p_M_D <= non_literals.p_M_D).sum() / len(books)
    print(
        f"Fraction of higher ln p(M | D) results of literal and modular backends is {frac_neq_higher}."
    )

    metrics = ["p_M_D", "size"]
    groups = rs.groupby(level=["variant", "task"])[metrics]

    means = groups.mean()
    means = pd.DataFrame(means.stack()).rename(columns={0: "mean"})
    medians = groups.median()
    medians = pd.DataFrame(medians.stack()).rename(columns={0: "median"})
    maxs = groups.max()
    maxs = pd.DataFrame(maxs.stack()).rename(columns={0: "max"})

    table = means.join([medians, maxs])
    table = table.unstack(0)
    table.columns = table.columns.swaplevel(0, 1)
    table = table[table.columns[[0, 2, 4, 1, 3, 5]]]

    table.index = table.index.rename(["task", "metric"])
    table = table.reset_index()
    table["metric"] = table["metric"].apply(
        lambda s: "$K$" if s == "size" else "$\ln p(\MM \mid \DD)$")
    table.index = pd.MultiIndex.from_arrays([table["task"], table["metric"]])
    del table["task"]
    del table["metric"]
    table = table.sort_values("metric")
    table = table.reindex(
        ["generated_function", "sparse_noisy_data", "variable_noise", "sine"],
        level=0)

    table = table.round(2)
    # Slim table, only keep modular numbers since modular and literal are
    # equivalent.
    table = table[list(filter(lambda x: x[0] == "non_literal", table.columns))]

    dga = drugowitsch_ga.stack()
    dga.index = dga.index.swaplevel(0, 1)
    dga = dga.rename("Drugowitsch")
    dga.index = dga.index.rename(["task", "metric"])

    table = table.join(dga)

    print(table)
    print()

    print(table.to_latex(escape=False))
    print()

    print("Comparing impact of different data seeds (only non-literal)")

    rs = rs.set_index("params.data.seed", append=True)
    groups = rs.groupby(level=["variant", "task", "params.data.seed"])[metrics]
    means = groups.mean()
    means = pd.DataFrame(means.stack()).rename(columns={0: "mean"})
    medians = groups.median()
    medians = pd.DataFrame(medians.stack()).rename(columns={0: "median"})
    maxs = groups.max()
    maxs = pd.DataFrame(maxs.stack()).rename(columns={0: "max"})

    means = means.unstack(2).loc["non_literal"]

    print(means)

    print("Std of means across data sets")
    print(means.std(axis=1))

    medians = medians.unstack(2).loc["non_literal"]

    print(medians)

    print("Std of medians across data sets")
    print(medians.std(axis=1))


def median_run(runs, metric, algorithm, variant, task):
    rs = runs.loc[(algorithm, variant, task)]

    assert len(rs) == reps * 5, len(rs)
    r = rs[rs[metric] == rs[metric].quantile(interpolation="higher")].iloc[0]
    return r


def plot_median_predictions(runs, path, graphs):
    print()
    print(
        "## Plotting median ln p(M | D) (or MAE) run for all algorithms and each "
        "task to compare plots")
    print()

    exp_names = runs.unstack().index

    prediction_plots = {}
    for exp_name in exp_names:
        algorithm, variant, task = exp_name
        if algorithm == "xcsf":
            metric = "metrics.mae"
            rs = runs
        else:
            metric = "metrics.elitist.p_M_D"
            rs = keep_unstandardized(runs)

        # TODO Not that nice, this. Maybe plot median of standardized runs by
        # themselves, too?
        # Since we have some experiments that were only standardized runs, we
        # have to shortcut here sometimes.
        if (exp_name == ('berbl', 'standardized', 'generated_function')
            or exp_name == ('berbl', 'standardized', 'sparse_noisy_data')):
            continue

        r = median_run(rs, metric, algorithm, variant, task)

        print(f"Plotting median run for {'.'.join(exp_name)} …")
        prediction_plots |= {exp_name: r}

        fixed_art_uri = fix_artifact_uri(r["artifact_uri"], path)

        rdata = get_data(fixed_art_uri)

        fig, ax = plt.subplots()
        plot_training_data(ax, fixed_art_uri)
        plot_prediction(ax, fixed_art_uri)
        ax.set_xlabel("Input x")
        ax.set_ylabel("Output y")
        save_plot("gecco2022", ".".join(exp_name), "pred", fig)

        if graphs:
            plt.show()
        else:
            plt.close("all")


def stat_tests_lit_mod(runs):
    print()
    print("# Performing statistical tests for literal vs. modular")
    print()

    runs = keep_unstandardized(runs)

    print("Keeping only reproduction BERBL experiments …")
    # First level of index is algorithm.
    rs = runs.loc["berbl"]
    # Second level of index is variant.
    rs = rs.loc[["book", "non_literal"]]

    assert len(rs) == reps * 5 * (4 + 4)

    rs = rs.rename(lambda s: s.removeprefix("metrics.elitist."), axis=1)

    means = rs.groupby(["variant", "task"]).mean()[metrics.keys()]
    for metric, higher_better in metrics.items():
        probs, fig = stat_test(means.loc["book"][metric],
                               means.loc["non_literal"][metric],
                               rope=ropes[metric],
                               plot=True)
        save_plot("gecco2022", "stat", f"literal-vs-modular-{metric}", fig)
        print_stat_results("lit", "mod", metric, probs, ropes[metric],
                           higher_better)
        print()


def table_stat_tests_berbl_xcsf(runs):
    print()
    print("# Comparison of BERBL with XCSF (MAE)")
    print()

    metric = "mae"

    print("Selecting interval-based runs …")
    rs_interval = runs[runs["params.match"] == "softint"]
    rs_interval = keep_unstandardized(rs_interval)

    rs_book = runs.loc[("berbl", "book")]
    rs_book = keep_unstandardized(rs_book)

    assert len(rs_interval) == 2 * len(rs_book), (
        "There are params.matching==softint runs lacking for some "
        f"experiments ({len(rs_interval)} != {2 * len(rs_book)})")

    rs_lit = rs_interval[rs_interval["params.literal"] == "True"]
    rs_mod = rs_interval[rs_interval["params.literal"] == "False"]
    assert len(rs_lit) == len(rs_mod), ("Different number of runs for "
                                        f"interval-based literal ({len(rs_lit)}) and "
                                        f"modular ({len(rs_mod)})")

    groups_lit = rs_lit.sort_values("task").groupby(
        "task")[f"metrics.elitist.{metric}"]
    groups_mod = rs_mod.sort_values("task").groupby(
        "task")[f"metrics.elitist.{metric}"]
    groups_xcsf = runs.loc[("xcsf", "book")].groupby(["task"
                                                      ])[f"metrics.{metric}"]

    table = pd.DataFrame()
    for grp, f in [
        (groups, f) for f in [np.mean, np.std]
            for groups in [("literal",
                            groups_lit), ("modular",
                                          groups_mod), ("xcsf", groups_xcsf)]
    ]:
        name, groups = grp
        table = table.append(groups.agg(f).rename(f"{name}###{f.__name__}"))

    table.index = table.index.map(lambda x: tuple(x.split("###")))
    table.index = table.index.rename(["algorithm", "statistic"])
    table = table.T
    # TODO Store list of experiments/numbers/order at the toplevel
    table = table.reindex(
        ["generated_function", "sparse_noisy_data", "variable_noise", "sine"])
    table = table.sort_values(by="algorithm", axis=1)

    print(table)
    print()

    table_rounded = table.copy()
    for variant, statistic in table.keys():
        if statistic == "std":
            table_rounded[(variant,
                           statistic)] = table_rounded[(variant,
                                                        statistic)].round(2)
        else:
            table_rounded[(variant,
                           statistic)] = table_rounded[(variant,
                                                        statistic)].round(4)

    table_rounded = table_rounded[["modular", "xcsf"]]

    print(table_rounded.to_latex())
    print()

    print()
    print("## Statistical comparison of BERBL with XCSF (MAE)")
    print()

    for variant in ["literal", "modular"]:
        probs, fig = stat_test(table[("xcsf", "mean")],
                               table[(variant, "mean")],
                               rope=ropes[metric],
                               plot=True)
        save_plot("gecco2022", "stat", f"xcsf-vs-{variant}-{metric}", fig)
        print_stat_results(
            "XCSF",
            variant,
            metric,
            probs,
            ropes[metric],
            # Lower MAE are better.
            higher_better=False)
        print()


def plot_extra_xcsf_prediction(runs, path, task, graphs):
    print()
    print("## Plotting XCSF prediction (median run re MAE) on data seed of "
          "BERBL median run")
    print()

    data_seed = median_run(keep_unstandardized(runs), "metrics.elitist.p_M_D",
                           "berbl", "non_literal",
                           task)["params.data.seed"]

    exp_name = f"xcsf.book.{task}"

    rs_xcsf = runs.loc[("xcsf", "book", task)]
    rs_xcsf = rs_xcsf[rs_xcsf["params.data.seed"] == data_seed]
    metric = "metrics.mae"
    # TODO Ugly that we hardcode "mlruns/" here
    r = rs_xcsf[rs_xcsf[metric] == rs_xcsf[metric].quantile(
        interpolation="higher")].iloc[0]
    rid = r["run_id"]
    fixed_art_uri = fix_artifact_uri(r["artifact_uri"], path)
    rdata = get_data(fixed_art_uri)

    fig, ax = plt.subplots()
    plot_training_data(ax, fixed_art_uri)
    plot_prediction(ax, fixed_art_uri)
    ax.set_xlabel("Input x")
    ax.set_ylabel("Output y")
    save_plot("gecco2022", exp_name, f"pred-same-data-berbl", fig)

    if graphs:
        plt.show()
    else:
        plt.close("all")


def plot_berbl_pred_dist(runs, path, task, graphs):
    print()
    print("## Plotting BERBL predictive distribution")
    print()

    exp_name = f"berbl.non_literal.{task}"
    r = median_run(keep_unstandardized(runs), "metrics.elitist.p_M_D", "berbl",
                   "non_literal", task)

    # index 4 corresponds to p(y | x = 0.25), see
    # experiments.berbl.BERBLExperiment.evaluate.
    place = 0.25
    index = 4
    print(
        f"Plotting point distribution at y={place} of median ln p(M | D) run for "
        f"{exp_name}")
    rid = r["run_id"]
    fixed_art_uri = fix_artifact_uri(r["artifact_uri"], path)
    rdata = get_data(fixed_art_uri)
    mean = rdata["y_points_mean"].loc[index][0]
    std = rdata["y_points_std"].loc[index][0]
    y = rdata[f"y_points_{index}"]
    pdf = rdata[f"prob_y_points_{index}"]

    fig, ax = plt.subplots()
    std1 = mean - std
    std2 = mean + std

    ax.plot(y, pdf, "C0--")
    ax.axvline(mean, color="C0")
    ax.fill_between(x=y.to_numpy().ravel(),
                    y1=pdf.to_numpy().ravel(),
                    color="C0",
                    alpha=0.3,
                    where=np.logical_and(std1 < y,
                                         y < std2).to_numpy().ravel())

    # Roughly approximate std indexes (suffices for drawing the figure).
    idx = np.where(np.logical_and(std1 < y, y < std2))[0]
    stdidx1 = idx[0]
    stdidx2 = idx[-1]
    ax.vlines([y.loc[stdidx1], y.loc[stdidx2]],
              ymin=0,
              ymax=[pdf.loc[stdidx1], pdf.loc[stdidx2]],
              linestyle="dotted",
              color="C0")

    ax.set_xlabel("Output y")
    ax.set_ylabel(f"ln p(y | x = {place})")
    save_plot("gecco2022", exp_name, f"dist-{place}", fig)

    if graphs:
        plt.show()
    else:
        plt.close("all")


# Name of task and whether soft interval matching is used.
berbl_experiments = [
    "book.generated_function",
    "book.sparse_noisy_data",
    "book.sine",
    "book.variable_noise",
    # Not in the book but required for fairer comparison with XCSF.
    "additional_literal.generated_function",
    "additional_literal.sparse_noisy_data",
    # Expected to behave the same as the literal implementation.
    "non_literal.generated_function",
    "non_literal.sparse_noisy_data",
    "non_literal.sine",
    "non_literal.variable_noise",
    # Not in the book but required for fairer comparison with XCSF.
    "additional_non_literal.generated_function",
    "additional_non_literal.sparse_noisy_data",
]
xcsf_experiments = [
    "book.generated_function",
    "book.sparse_noisy_data",
    "book.sine",
    "book.variable_noise",
]


@click.command()
@click.argument("PATH")
@click.option("--graphs/--no-graphs",
              default=False,
              help="Whether to show all plots and graphs",
              show_default=True)
@click.option("--commit",
              default=None,
              help="Only consider runs that ran from this commit",
              show_default=True)
def main(path, graphs, commit):
    """
    Analyse the parameter search results found at PATH (PATH is expected to be
    an mlflow tracking URI, e.g. an mlruns folder).
    """
    mlflow.set_tracking_uri(path)

    berbl_experiment_names = [
        f"berbl.{exp_name}" for exp_name in berbl_experiments
    ]
    berbl_experiments_standardized_names = [
        "berbl.standardized.generated_function",
        "berbl.standardized.sparse_noisy_data",
    ]
    xcsf_experiment_names = [
        f"xcsf.{exp_name}" for exp_name in xcsf_experiments
    ]
    exp_names = (berbl_experiment_names + berbl_experiments_standardized_names
                 + xcsf_experiment_names)

    # runs = read_mlflow(exp_names, commit=commit, check_finished=False)
    runs = read_mlflow(exp_names, commit=commit)

    print(runs.groupby(level=["algorithm", "variant", "task"]).agg(len))
    n_runs = (
        # BERBL experiments (4 from book, 4 from book with modular backend, 2
        # additional each with interval-based matching).
        (
            4 + 4 + 2 + 2
            # BERBL experiments with standardization.
            + 4
            # XCSF experiments.
            + 4)
        # 5 data seeds per experiment.
        * 5
        # reps runs.
        * reps)
    assert len(
        runs) == n_runs, f"Expected {n_runs} runs but there were {len(runs)}"

    table_compare_drugowitsch(runs)

    plot_median_predictions(runs, path, graphs)

    stat_tests_lit_mod(runs)

    table_stat_tests_berbl_xcsf(runs)

    plot_extra_xcsf_prediction(runs, path, "generated_function", graphs)
    plot_extra_xcsf_prediction(runs, path, "sparse_noisy_data", graphs)
    plot_extra_xcsf_prediction(runs, path, "variable_noise", graphs)
    plot_extra_xcsf_prediction(runs, path, "sine", graphs)

    plot_berbl_pred_dist(runs, path, "generated_function", graphs)
    plot_berbl_pred_dist(runs, path, "sparse_noisy_data", graphs)
    plot_berbl_pred_dist(runs, path, "variable_noise", graphs)
    plot_berbl_pred_dist(runs, path, "sine", graphs)

    # TODO Perform statistical tests on standardized data, too


if __name__ == "__main__":
    main()
