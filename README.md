# The berbl-eval library


This package has two purposes.

1. It's a library that interfaces with mlflow to help in extracting data logged
   during experiments using the [berbl experiments
   library](https://github.com/berbl-dev/berbl-exp).
2. It contains the scripts (in the [scripts directory](scripts/)) that were used
   to perform the statistical evaluation for the following publications:

   - Pätzel, Hähner. 2022. *The Bayesian Learning Classifier System:
     Implementation, Replicability, Comparison with XCSF*.
     [DOI](https://doi.org/10.1145/3512290.3528736).


## Running the experiments


We'll exemplarily show how to run the statistical evaluation for the 2022 GECCO
paper ([this script](scripts/gecco2022.py)). Other scripts can be run
analogously.


1. Install
   [Nix](https://nixos.org/manual/nix/stable/installation/installing-binary.html)
   [including flakes support](https://nixos.wiki/wiki/Flakes) in order to be
   able to run `nix develop` later.  Note that [Nix does not yet support
   Windows](https://nixos.org/manual/nix/stable/installation/supported-platforms.html).
2. Clone the repository (`git clone …`). Run the next steps from within the
   cloned repository.
3. Enter a shell that contains all dependencies by running
   ```bash
   nix develop
   ```
   (may take some time to complete).
4. Run the evaluation script, pointing it to the `mlruns` directory containing the
   experiment results.
   ```bash
   python scripts/gecco2022.py path/to/results/mlruns
   ```


Note: Some evaluation data is printed to `stdout`, some is stored in `eval/gecco2022`.


<!-- Local Variables: -->
<!-- mode: markdown -->
<!-- End: -->
