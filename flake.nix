{
  description = "A flake for building the berbl-eval library";

  inputs.pystan.url = "github:dpaetzel/flake-pystan-2.19.1.1";
  inputs.baycomp.url = "github:dpaetzel/flake-baycomp";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-21.11";
  inputs.overlays.url = "github:dpaetzel/overlays";

  outputs = { self, nixpkgs, overlays, pystan, baycomp }: {

    defaultPackage.x86_64-linux = with import nixpkgs {
      system = "x86_64-linux";
      overlays = with overlays.overlays; [ mlflow pandas ];
    };
      python3.pkgs.buildPythonPackage rec {
        pname = "berbl-eval";
        version = "0.1.0";

        src = self;

        propagatedBuildInputs = with python3.pkgs; [
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
  };
}
