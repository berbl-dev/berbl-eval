import warnings

import click
import cmpbayes
import scipy.stats as st
from berbl.eval import *
from berbl.eval.plot import *
from berbl.eval.drugowitsch import drugowitsch_ga

warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)
import matplotlib

matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42

pd.options.display.max_rows = 2000

# Metric and whether higher is better.
metrics = {"p_M_D": True, "mae": False, "size": False}
ropes = {"p_M_D": 10, "mae": 0.01, "size": 0.5}

reps = 10


@click.command()
@click.argument("PATH")
@click.option("--latex/--no-latex",
              help="Generate LaTeX output (tables etc.)",
              default=False)
def main(path, latex):
    """
    Analyse GECCO 2022-style results statistically for hitting the metric values
    reported by Drugowitsch quick'n'dirtily.
    """
    runs = read_runs(path)

    runs = keep_unstandardized(runs)

    print(runs.groupby(level=["algorithm", "variant", "task"]).agg(len))
    n_runs = (
        # BERBL experiments (4 from book, 4 from book with modular backend, 2
        # additional each with interval-based matching).
        (4 + 4 + 2 + 2)
        # 5 data seeds per experiment.
        * 5
        # reps runs.
        * reps)
    assert len(
        runs) == n_runs, f"Expected {n_runs} runs but there were {len(runs)}"

    # First level of index is algorithm.
    rs = runs.loc["berbl"]
    # Second level of index is variant.
    rs = rs.loc[["book", "non_literal"]]

    assert len(rs) == reps * 5 * (4 + 4)

    rs = rs.rename(lambda s: s.removeprefix("metrics.elitist."), axis=1)
    hdis = {}
    for task_name in runs.index.levels[2]:
        metric_name = "metrics.elitist.p_M_D"
        # TODO metric_name = "metrics.elitist.size"

        rs = runs.loc["berbl", "book", task_name]

        def analyse(rs_):
            metric_values = rs_.to_numpy().ravel()
            # This is a bit hacky: We use a Kruschke model with two times the
            # same data. This way we don't need to program an entirely new
            # model; we simply only consider one of the two sets of
            # distributions being sampled. Of course this means that some of the
            # things in the fitted model are not meaningful (e.g. the \*minus\*
            # distributions).
            model = cmpbayes.Kruschke(metric_values,
                                      metric_values).fit(num_samples=50000,
                                                         random_seed=1)

            sample = model.data_.posterior_predictive.y1_rep.to_numpy().ravel()

            sample_ = sorted(sample)
            hdi_percent = 99
            hdi_lower = ((1 - hdi_percent / 100) / 2)
            hdi_upper = 1 - hdi_lower
            i_lower = int(np.floor(len(sample) * hdi_lower))
            i_upper = int(np.ceil(len(sample) * hdi_upper))
            hdi = (sample_[i_lower], sample_[i_upper])
            return hdi

        hdis[task_name] = rs.groupby("params.data.seed")[metric_name].agg(
            analyse)

    res = pd.DataFrame(hdis).append(drugowitsch_ga.iloc[0])

    smart_print(res, latex=latex)
    print(
        "Warning: This was a quick'n'dirty analysis I conducted on a flight. "
        "What are these HDIs exactly? 99% HDIs of the mean? Or 99% HDIs of "
        "where a single run will end up?")


if __name__ == "__main__":
    main()
