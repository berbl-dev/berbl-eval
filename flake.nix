{
  description = "The berbl-eval library";

  # 2022-01-24
  inputs.nixpkgs.url =
    "github:NixOS/nixpkgs/8ca77a63599ed951d6a2d244c1d62092776a3fe1";

  inputs.baycomp.url = "github:dpaetzel/baycomp";
  inputs.cmpbayes.url = "github:dpaetzel/cmpbayes";
  inputs.overlays.url = "github:dpaetzel/overlays";

  outputs = { self, nixpkgs, baycomp, cmpbayes, overlays }:
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
          packages."${system}".fetser

          cmpbayes.defaultPackage."${system}"
          baycomp.packages."${system}".baycomp
          matplotlib
          mlflow
          networkx
          numpy # 1.21.2
          pandas

          python
          ipython

          # We use ugly venvShellHook here because packaging pystan/httpstan is
          # not entirely straightforward.
          venvShellHook
        ];

        venvDir = "./_venv";

        postShellHook = ''
          unset SOURCE_DATE_EPOCH

          export LD_LIBRARY_PATH="${
            lib.makeLibraryPath [ stdenv.cc.cc ]
          }:$LD_LIBRARY_PATH";
          PYTHONPATH=$PWD/$venvDir/${python.sitePackages}:$PYTHONPATH
        '';

        postVenvCreation = ''
          unset SOURCE_DATE_EPOCH
          pip install pystan==3.4.0
        '';
      };

      packages."${system}".fetser = stdenv.mkDerivation {
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
