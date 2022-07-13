{
  description = "The berbl-eval library";

  # 2022-01-24
  inputs.nixpkgs.url =
    # "github:NixOS/nixpkgs/8ca77a63599ed951d6a2d244c1d62092776a3fe1";
    # From cmpbayes, 2022-02-21.
    "github:nixos/nixpkgs/af04d4eb146cb3784c883a76997613f2524e310e";

  inputs.baycomp.url = "github:dpaetzel/baycomp";
  inputs.baycomp.inputs.nixpkgs.follows = "nixpkgs";
  inputs.cmpbayes.url = "github:dpaetzel/cmpbayes";
  inputs.cmpbayes.inputs.nixpkgs.follows = "nixpkgs";

  outputs = { self, nixpkgs, baycomp, cmpbayes }:
    let system = "x86_64-linux";
    in with import nixpkgs {
      inherit system;
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
          numpy
          pandas

          python
          ipython
        ];
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

      devShell.${system} = pkgs.mkShell {

        # We use ugly venvShellHook here because packaging pystan/httpstan is
        # not entirely straightforward.
        packages =
          with python.pkgs;
          [ ipython python venvShellHook ]
          ++ [ defaultPackage."${system}"
               packages."${system}".fetser
             ];

        venvDir = "./_venv";

        postShellHook = ''
          unset SOURCE_DATE_EPOCH

          PYTHONPATH=$PWD/$venvDir/${python.sitePackages}:$PYTHONPATH
        '';

        # Using httpstan==4.7.2 (the default as of 2022-06-10) leads to a
        # missing symbols error on NixOS. 4.7.1 works, however, so we use that.
        postVenvCreation = ''
          unset SOURCE_DATE_EPOCH
          pip install httpstan==4.7.1 pystan==3.4.0
        '';

      };
    };
}

# TODO Swap to setup.cfg pyproject.toml layout
