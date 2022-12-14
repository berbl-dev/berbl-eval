{
  description = "The berbl-eval library";

  inputs = {
    berbl-exp.url = "github:berbl-dev/berbl-exp/simplify-running-experiments";

    baycomp.url = "github:dpaetzel/baycomp";
    baycomp.inputs.nixpkgs.follows = "berbl-exp/berbl/nixos-config/nixpkgs";
    # cmpbayes.url = "github:dpaetzel/cmpbayes";
    # cmpbayes.inputs.nixpkgs.follows = "nixpkgs";
    cmpbayes = {
      type = "path";
      inputs.nixos-config.follows = "berbl-exp/berbl/nixos-config";
      path = "/home/david/Code/cmpbayes";
    };
  };

  outputs = { self, berbl-exp, baycomp, cmpbayes }:
    let
      system = "x86_64-linux";
      nixpkgs = berbl-exp.inputs.berbl.inputs.nixos-config.inputs.nixpkgs;
      pkgs = import nixpkgs { inherit system; };
      # TODO Instead of hardcoding the Python version here, it should be
      # provided to defaultPackage sensibly (e.g. by allowing some sort of
      # override)?
      python = pkgs.python310;
    in rec {

      defaultPackage."${system}" = python.pkgs.buildPythonPackage rec {
        pname = "berbl-eval";
        version = "0.1.0";

        src = self;

        # We use pyproject.toml.
        format = "pyproject";

        # TODO In order to provide a proper default flake here we need to
        # package pystan/httpstan properly (>= version 3.4.0). For now, we
        # assume that pystan is already there.
        postPatch = ''
          sed -i "s/^.*pystan.*$//" setup.cfg
        '';

        propagatedBuildInputs = with python.pkgs; [
          cmpbayes.defaultPackage."${system}"
          baycomp.defaultPackage."${system}"
          matplotlib
          mlflow
          networkx
          numpy
          pandas

          ipython

          scikit-learn
          deap
        ];
      };

      packages."${system}".fetser = pkgs.stdenv.mkDerivation {
        pname = "fetser";
        version = "1.0.0";
        src = self;

        buildPhase = "";
        installPhase = ''
          mkdir -p $out/bin
          cp fetch-results $out/bin
          cp serve-results $out/bin
        '';

        propagatedBuildInputs = [ python.pkgs.mlflow ];
      };

      devShell.${system} = pkgs.mkShell {

        packages = [
          python.pkgs.ipython
          (python.withPackages (p: [ defaultPackage."${system}" ]))
          python.pkgs.venvShellHook
          packages."${system}".fetser
        ];

        # We use ugly venvShellHook here because packaging pystan/httpstan is
        # not entirely straightforward.
        venvDir = "./_venv";

        postShellHook = ''
          unset SOURCE_DATE_EPOCH

          export LD_LIBRARY_PATH="${
            pkgs.lib.makeLibraryPath [ pkgs.stdenv.cc.cc ]
          }:$LD_LIBRARY_PATH";
        '';
        # Seems not to be required any more.
        # PYTHONPATH=$PWD/$venvDir/${python.sitePackages}:$PYTHONPATH

        # Using httpstan==4.7.2 (the default as of 2022-06-10) leads to a
        # missing symbols error on NixOS. 4.7.1 works, however, so we use that.
        postVenvCreation = ''
          unset SOURCE_DATE_EPOCH
          pip install httpstan==4.7.1 pystan==3.4.0
        '';

      };
    };
}
