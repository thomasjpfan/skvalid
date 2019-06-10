import pytest

from skvalid.parameters import TypeOf
from skvalid.parameters import Enum
from skvalid.parameters import Union
from skvalid.parameters import Interval
from skvalid.parameters import Const

from skvalid.validator import validate_paramters


@pytest.mark.parametrize("params", [{
    "penalty": "l2",
    "dual": True
}, {
    "tol": 0.01,
    "solver": "sag"
}])
def test_validator_parameters_exist(params):
    config = {
        "penalty": Union(Enum("l1", "l2", "elasticnet", "none")),
        "dual": TypeOf(bool),
        "tol": Interval(float, 0.0, None, lower_inclusive=False),
        "solver": Enum("newton-cg", "lbfgs", "liblinear", "sag", "saga")
    }
    # does not raise
    validate_paramters(config, **params)


@pytest.mark.parametrize("params, error_key", [
    ({
        "penalty2": "l1"
    }, "penalty2"),
    ({
        "penalty": "none",
        "dual2": True,
    }, "dual2"),
    ({
        "C2": 0.0,
        "solver": "lbfgs",
        "fit_intercept": False
    }, "C2"),
])
def test_validator_parameters_not_exist(params, error_key):
    config = {
        "penalty": Union(Enum("l1", "l2", "elasticnet", "none")),
        "dual": TypeOf(bool),
        "C": Interval(float, 0.0, None),
        "fit_intercept": True
    }
    msg = "{} is not a valid parameter".format(error_key)
    with pytest.raises(KeyError, match=msg):
        validate_paramters(config, **params)


@pytest.mark.parametrize("params", [{
    "penalty": "hello"
}, {
    "dual": 1.0
}, {
    "tol": 0.0
}, {
    "solver": "sagone"
}, {
    "warn_start": 4
}, {
    "n_jobs": "boom"
}])
def test_validator_parameters_validate_error(params):
    config = {
        "penalty": Union(Enum("l1", "l2", "elasticnet", "none")),
        "dual": TypeOf(bool),
        "tol": Interval(float, 0.0, None, lower_inclusive=False),
        "solver": Enum("newton-cg", "lbfgs", "liblinear", "sag", "saga"),
        "warm_start": TypeOf(bool),
        "n_jobs": Union(Interval(int, 1, None), Const(-1), Const(None))
    }
    with pytest.raises(Exception):
        validate_paramters(config, **params)


@pytest.mark.parametrize("params", [{
    "kernel": "poly",
    "degree": 4,
    "gamma": "auto"
}, {
    "kernel": "rbf",
    "gamma": 0.4
}, {
    "kernel": "sigmoid",
    "coef0": 0.4,
    "tol": 1.0
}])
def test_validator_conditions_exists(params):
    config = {
        "kernel": Enum("linear", "poly", "rbf", "sigmoid", "percomputed"),
        "degree": Interval(int, 1, None),
        "gamma": Union(Interval(float, 0, None), Const("auto")),
        "coef0": Interval(float, 0.0, None),
        "tol": Interval(float, 0.0, None, lower_inclusive=False),
        "_conditions": {
            "kernel": {
                "poly": ["degree", "gamma", "coef0"],
                "rbf": ["gamma"],
                "sigmoid": ["gamma", "coef0"]
            }
        }
    }
    validate_paramters(config, **params)


@pytest.mark.parametrize("params, msg", (({
    "kernel": "rbf",
    "degree": 4,
}, "kernel: rbf, not compatible with degree"), ({
    "kernel": "rbf",
    "coef0": 0.0,
    "degree": 3
}, "kernel: rbf, not compatible with coef0"), ({
    "kernel": "sigmoid",
    "degree": 5,
    "tol": 0.1
}, "kernel: sigmoid, not compatible with degree")))
def test_validator_conditions_error(params, msg):
    config = {
        "kernel": Enum("linear", "poly", "rbf", "sigmoid", "percomputed"),
        "degree": Interval(int, 1, None),
        "gamma": Union(Interval(float, 0, None), Const("auto")),
        "coef0": Interval(float, 0.0, None),
        "tol": Interval(float, 0.0, None, lower_inclusive=False),
        "_conditions": {
            "tol": {},
            "kernel": {
                "poly": ["degree", "gamma", "coef0"],
                "rbf": ["gamma"],
                "sigmoid": ["gamma", "coef0"]
            }
        }
    }
    with pytest.raises(ValueError, match=msg):
        validate_paramters(config, **params)
