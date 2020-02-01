skvalid
===========

Lightweight scikit-learn validation framework. The documentation can be found 
`here <https://skvalid.readthedocs.io/en/latest/>`_.

.. image:: https://circleci.com/gh/thomasjpfan/skvalid.svg?style=shield
    :target: https://circleci.com/gh/thomasjpfan/skvalid
    :alt: CI Status

.. image:: https://codecov.io/gh/thomasjpfan/skvalid/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/thomasjpfan/skvalid
    :alt: Codecov Status

Validation
..........

In this example, we define the valid parameters for scikit-learn's 
``LogesticRegression``:

.. code-block:: python

    from skvalid import Interval, TypeOf, Union, Enum, Const
    from numpy.random import RandomState
    import numbers

    valid_params = {
        "penalty": Enum("l2", "l1", "elasticnet", "none"),
        "dual": TypeOf(bool),
        "tol": Interval(float, lower=0, upper=None, lower_inclusive=False),
        "C": Interval(float, lower=0),
        "fit_intercept": TypeOf(bool),
        "class_weight": Union(TypeOf(dict), Enum('balanced', None)),
        "random_state": TypeOf(int, RandomState, type(None)),
        "solver": Enum("newton-cg", "lbfgs", "liblinear", "sag", "saga", "warn"),
        "max_iter": Interval(int, lower=0),
        "multi_class": Enum("ovr", "multinomial", "auto", "warn"),
        "verbose": Interval(int, lower=0, tags=["control"]),
        "warm_start": TypeOf(bool, tags=["control"]),
        "n_jobs": Union(Interval(int, lower=1, upper=None), Enum(-1, None), tags=["resource"]),
        "l1_ratio": Union(Interval(float, lower=0, upper=1), Const(None)),
        "intercept_scaling": TypeOf(numbers.Real)
    }

With this configuration, we can validate a set of parameters:

.. code-block:: python

    from skvalid import validate_parameters
    validate_parameters(lr_config, dict(penalty="l2"))
    # Does not raise

The following will raise an error:

.. code-block:: python

    validate_parameters(lr_config, dict(penalty="l3"))
    # ValueError: penalty: l3 is not in [l2, l1, elasticnet, none]

    validate_parameters(lr_config, dict(warm_start="bad"))
    # TypeError: warm_start: Bad is not a bool

    validate_parameters(lr_config, dict(random_state=2.3))
    # TypeError: random_state: 2.3 is not a int or RandomState or NoneType

    validate_parameters(lr_config, dict(class_weight="unbalanced"))
    # ValueError: class_weight: unbalanced is not a dict, unbalanced is not in [balanced, None]

    validate_parameters(lr_config, dict(tol=-1.3))
    # ValueError: tol: -1.3 not in (0, inf)    

    validate_parameters(lr_config, dict(max_iter=-3))
    # ValueError: max_iter: -3 not in [0, inf)

Integration with scikit-learn's LogisticRegression
..................................................

This light parameter definition scheme can be integrated into scikit-learn's 
``LogisticRegression`` as follows:

.. code-block:: python

    class LogisticRegression(...):
        
        valid_params = {
            "penalty": Enum("l2", "l1", "elasticnet", "none"),
            "dual": TypeOf(bool),
            "tol": Interval(float, lower=0, upper=None, lower_inclusive=False),
            "C": Interval(float, lower=0),
            "fit_intercept": TypeOf(bool),
            "class_weight": Union(TypeOf(dict), Enum('balanced', None)),
            "random_state": TypeOf(int, RandomState, type(None)),
            "solver": Enum("newton-cg", "lbfgs", "liblinear", "sag", "saga", "warn"),
            "max_iter": Interval(int, lower=0),
            "multi_class": Enum("ovr", "multinomial", "auto", "warn"),
            "verbose": Interval(int, lower=0, tags=["control"]),
            "warm_start": TypeOf(bool, tags=["control"]),
            "n_jobs": Union(Interval(int, lower=1, upper=None), Enum(-1, None), tags=["resource"]),
            "l1_ratio": Union(Interval(float, lower=0, upper=1), Const(None)),
            "intercept_scaling": TypeOf(numbers.Real)
        }
        
        def fit(self, X, ...):
            validate_parameters(self.valid_params, self.get_params())

There will be checks in the tests to make sure ``valid_params`` and the 
parameters are consistent. 

Tagging
-------

The tags allow us to define what each parameter is used for. The default 
``tag`` is `tuning` which means this parameter is good to hyperparameter 
search. ``n_jobs`` controls the number of resources, thus it has a 
``resource`` tag. We can have some parameters be tagged as ``warm_start``
parameters. 


Installation
............

You can install skvalid directly from pypi:

.. code-block:: bash

    pip install git+https://github.com/thomasjpfan/skvalid

Development
...........

The development version can be installed by running ``make dev``. Then we can lint ``make lint`` and tests by running ``pytest``.
