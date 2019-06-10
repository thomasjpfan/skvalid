skvalid
===========

Lightweight scikit-learn validation framework. The documentation is hosted at `ReadTheDocs <https://skvalid.readthedocs.io/en/latest/>`_.

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

    lr_config = {
        "penalty": Enum("l2", "l1", "elasticnet", "none"),
        "dual": TypeOf(bool),
        "tol": Interval(float, 0, None, lower_inclusive=False),
        "C": Interval(float, 0),
        "fit_intercept": TypeOf(bool),
        "class_weight": Union(TypeOf(dict), Enum('balanced', None)),
        "random_state": TypeOf(int, RandomState, type(None)),
        "solver": Enum("newton-cg", "lbfgs", "liblinear", "sag", "saga"),
        "max_iter": Interval(int, 0),
        "multi_class": Enum("ovr", "multinomial", "auto"),
        "verbose": Interval(int, 0, tags=["control"]),
        "warm_start": TypeOf(bool, tags=["control"]),
        "n_jobs": Union(Interval(int, 1, None), Enum(-1, None), 
                        tags=["resource"]),
        "l1_ratio": Union(Interval(float, 0, 1), Const(None))
    }

With this configuration, we can validate a set of parameters:

.. code-block:: python

    from skvalid import validate_parameters
    validate_parameters(lr_config, penalty="l2") 
    # Does not raise

The following will raise an error:

.. code-block:: python

    validate_paramters(lr_config, penalty="l3")
    # ValueError: l3 is not in [l2, l1, elasticnet, none]

    validate_paramters(lr_config, warm_start="bad")
    # TypeError: Bad is not a bool

    validate_paramters(lr_config, random_state=2.3)
    # TypeError: 2.3 is not a int or RandomState or NoneType

    validate_paramters(lr_config, class_weight="unbalanced")
    # ValueError: unbalanced is not a dict, unbalanced is not 
    # in [balanced, None]

    validate_paramters(lr_config, tol=-1.3)
    # ValueError: -1.3 not in (0, inf)    

    validate_paramters(lr_config, max_iter=-3)
    # ValueError: -3 not in [0, inf)

Integration with scikit-learn's LogisticRegression
..................................................

This light parameter definition scheme can be integrated into scikit-learn's 
``LogisticRegression`` as follows:

.. code-block:: python

    class BaseEstimator:
        def _validate_params(self):
            if hasattr(self, "valid_params"):
                non_default_params = _non_default_params(self)
                validate_paramters(self.valid_params, non_default_params)

    class LogisticRegression(...):
        
        valid_params = {
            "penalty": Enum("l2", "l1", "elasticnet", "none"),
            "dual": TypeOf(bool),
            "tol": Interval(float, 0, None, lower_inclusive=False),
            "C": Interval(float, 0),
            "fit_intercept": TypeOf(bool),
            "class_weight": Union(TypeOf(dict), Const('balanced', None)),
            "random_state": TypeOf(int, RandomState, type(None)),
            "solver": Enum("newton-cg", "lbfgs", "liblinear", "sag", "saga"),
            "max_iter": Interval(int, 0),
            "multi_class": Enum("ovr", "multinomial", "auto"),
            "verbose": Interval(int, 0, tags=["control"]),
            "warm_start": TypeOf(bool, tags=["control"]),
            "n_jobs": Union(Interval(int, 1, None), Const(-1, None), 
                            tags=["resource"]),
            "l1_ratio": Union(Interval(float, 0, 1), Const(None))
        }
        
        def fit(self, X, ...):
            self._valid_params()

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
