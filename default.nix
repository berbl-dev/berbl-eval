{ lib, buildPythonPackage, mlflow, numpy, numpydoc, pandas, scipy
, sphinx }:

buildPythonPackage rec {
  pname = "berbl-eval";
  version = "0.1.0";

  src = ./.;

  propagatedBuildInputs =
    [ mlflow numpy numpydoc pandas scipy sphinx ];

  # testInputs = [ hypothesis pytest ];

  doCheck = false;

  meta = with lib; {
    description = "Helpers for evaluating BERBL experiments";
    license = licenses.gpl3;
  };
}
