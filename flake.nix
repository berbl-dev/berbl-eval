{
  description = "The berbl-eval library";

  # 2022-01-24
  inputs.nixpkgs.url =
    "github:NixOS/nixpkgs/8ca77a63599ed951d6a2d244c1d62092776a3fe1";
  inputs.pystan.url = "github:dpaetzel/flake-pystan-2.19.1.1";
  inputs.baycomp.url = "github:dpaetzel/flake-baycomp";
  inputs.overlays.url = "github:dpaetzel/overlays";

  outputs = { self, nixpkgs, overlays, pystan, baycomp }:
    with import nixpkgs {
      system = "x86_64-linux";
      overlays = with overlays.overlays; [ mlflow ];
    };
    let python = python39;
    in rec {

      defaultPackage.x86_64-linux = python.pkgs.buildPythonPackage rec {
        pname = "berbl-eval";
        version = "0.1.0";

        src = self;

        propagatedBuildInputs = with python.pkgs; [
          baycomp.packages.x86_64-linux.baycomp
          mlflow
          numpy
          numpydoc
          pandas
          pystan.packages.x86_64-linux.pystan
          scipy
          sphinx
        ];

        doCheck = false;

        meta = with lib; {
          description = "Helpers for evaluating BERBL experiments";
          license = licenses.gpl3;
        };
      };
      mlflowShell = mkShell {
        packages = [ python.pkgs.mlflow ];
      };
    };
}
