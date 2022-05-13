{
  description = "The berbl-eval library";

  # 2022-01-24
  inputs.nixpkgs.url =
    "github:NixOS/nixpkgs/8ca77a63599ed951d6a2d244c1d62092776a3fe1";
  inputs.baycomp.url = "github:dpaetzel/baycomp/add-flake-nix";
  inputs.overlays.url = "github:dpaetzel/overlays";

  outputs = { self, nixpkgs, overlays, baycomp }:
    let system = "x86_64-linux";
    in with import nixpkgs {
      inherit system;
      overlays = with overlays.overlays; [ mlflow ];
    };

    let python = python39;
    in rec {

      defaultPackage."${system}" = python.pkgs.buildPythonPackage rec {
        pname = "berbl-eval";
        version = "0.1.0";

        src = self;

        # TODO In order to provide a proper default flake here we need to
        # package pystan/httpstan properly (>= version 3.4.0). For now, we
        # assume that pystan is already there.
        postPatch = ''
          sed -i "s/^.*pystan.*$//" setup.py
        '';

        propagatedBuildInputs = with python.pkgs; [
          baycomp.packages."${system}".baycomp
          mlflow
          numpy # 1.21.2
          pandas

          # scipy
          # numpydoc
          # sphinx
        ];

        doCheck = false;

        meta = with lib; {
          description = "Helpers for evaluating BERBL experiments";
          license = licenses.gpl3;
        };
      };

      devShell."${system}" = mkShell {
        packages = [ python.pkgs.mlflow packages.fetser."${system}" ];
      };

      packages.fetser."${system}" = stdenv.mkDerivation {
        pname = "fetser";
        version = "1.0.0";
        src = self;

        buildPhase = "";
        installPhase = ''
          mkdir -p $out/bin
          cp fetch-results $out/bin
          cp serve-results $out/bin
        '';

        propagatedBuildInputs = [
          python.pkgs.mlflow
        ];
      };
    };
}

# TODO Swap to setup.cfg pyproject.toml layout
