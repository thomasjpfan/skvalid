import pytest
from numpy.random import RandomState

from skvalid.parameters import TypeOf
from skvalid.parameters import Enum
from skvalid.parameters import Union
from skvalid.parameters import Interval
from skvalid.parameters import Const
import typing


@pytest.mark.parametrize('type_of,value',
                         [(TypeOf(bool), True), (TypeOf(bool), False),
                          (TypeOf(typing.Callable), TypeOf.validate),
                          (TypeOf(float), 10.1), (TypeOf(int), 10),
                          (TypeOf(dict), {})])
def test_typeof_valid_values(type_of, value):
    type_of.validate(value, "tol")


@pytest.mark.parametrize('type_of,value', [(TypeOf(bool), 'Hello world'),
                                           (TypeOf(typing.Callable), True),
                                           (TypeOf(str), 120),
                                           (TypeOf(int), 10.1),
                                           (TypeOf(dict), True)])
def test_typeof_invalid_values(type_of, value):
    cur_type = type_of.types[0]
    name = getattr(cur_type, "__name__", str(cur_type))
    msg = 'tol: {} is not a {}'.format(value, name)
    with pytest.raises(TypeError, match=msg):
        type_of.validate(value, "tol")


def test_typeof_invalid_values_multiple():
    msg = 'tol: 4.0 is not a RandomState or int'
    with pytest.raises(TypeError, match=msg):
        TypeOf(RandomState, int).validate(4.0, "tol")


@pytest.mark.parametrize('constant,value', [(Const(4), 4),
                                            (Const('hehe'), 'hehe'),
                                            (Const(3.1), 3.1),
                                            (Const(True), True),
                                            (Const(None), None)])
def test_constant_valid_values(constant, value):
    # does not raise
    constant.validate(value, "tol")


@pytest.mark.parametrize('constant,value', [(Const(4), 3),
                                            (Const('hehe'), 'heh'),
                                            (Const(3.1), 4.1),
                                            (Const(True), False),
                                            (Const(None), 4),
                                            (Const(4), None)])
def test_constant_invalid_values(constant, value):
    msg = 'tol: {} != {}'.format(value, constant.value)
    with pytest.raises(ValueError, match=msg):
        constant.validate(value, "tol")


@pytest.mark.parametrize('members, msg',
                         [([], 'members must have at least one item'),
                          ((), 'members must have at least one item')])
def test_enum_invalid_members_init(members, msg):
    with pytest.raises(ValueError, match=msg):
        Enum(*members)


@pytest.mark.parametrize('enum, value',
                         [(Enum('a', 'b'), 'a'), (Enum('a', 'b'), 'b'),
                          (Enum('a', 'c', 'b'), 'c'),
                          (Enum('a', 1, None, 1.0, True), 'a'),
                          (Enum('a', 1, None, 1.0, True), 1),
                          (Enum('a', 1, None, 1.0, True), None),
                          (Enum('a', 1, None, 1.0, True), 1.0),
                          (Enum('a', 1, None, 1.0, True), True)])
def test_enum_values(enum, value):
    # does not raise
    enum.validate(value, "tol")


@pytest.mark.parametrize(
    'enum, value, msg',
    [(Enum('a', '5'), '3', r'3 is not in \[a, 5\]'),
     (Enum('a', '3', '9'), '5', r'5 is not in \[a, 3, 9\]'),
     (Enum('a', 1, None, 1.0,
           True), 'bad', r'bad is not in \[a, 1, None, 1.0, True\]')])
def test_enum_invalid_values(enum, value, msg):
    with pytest.raises(ValueError, match=msg):
        enum.validate(value, "tol")


def test_enum_invalid_type_error():
    enum, value, msg = Enum('hello', 'f'), 1, r'1 is not in \[hello, f\]'
    with pytest.raises(ValueError, match=msg):
        enum.validate(value, 'tol')


@pytest.mark.parametrize(
    'params, msg',
    [((), 'parameters must have at least one item'),
     (('hello', 'world'), 'all parameters must be of type Parameter'),
     ((TypeOf(int), 3), 'all parameters must be of type Parameter'),
     ((None, Enum('hello')), 'all parameters must be of type Parameter')])
def test_union_invalid_params_init(params, msg):
    with pytest.raises(ValueError, match=msg):
        Union(*params)


@pytest.mark.parametrize('union, value, msg', [
    (Union(TypeOf(int), Enum('hello', 'world')), None,
     r'tol: None is not a int and is not in \[hello, world\]'),
    (Union(TypeOf(int), Enum('hello', 'world')), 0.4, 'tol: 0.4 is not a int'),
])
def test_union_invalid_values(union, value, msg):
    with pytest.raises(ValueError, match=msg):
        union.validate(value, "tol")


@pytest.mark.parametrize('union, value', [
    (Union(TypeOf(int), Enum('hello', 'world')), 'hello'),
    (Union(TypeOf(int), Enum('hello', 'world')), 'world'),
    (Union(TypeOf(int), Enum('hello', 'world')), 10),
    (Union(TypeOf(int), Enum('hello', 'world'), Const(None)), None),
    (Union(TypeOf(float), TypeOf(int)), 10),
    (Union(TypeOf(float), TypeOf(int)), 10.3),
])
def test_union_valid_values(union, value):
    # does not raise
    union.validate(value, "tol")


def test_union_removes_tags():
    union = Union(TypeOf(int, tags=['control']),
                  Enum('a', 'b', tags=['not good']),
                  tags=['deprecated'])
    for params in union.params:
        assert not params.tags


@pytest.mark.parametrize('lower, upper, msg',
                         [(None, None, 'lower or upper must be defined'),
                          (10, 1, 'lower must be strictly less than upper'),
                          (10, 10, 'lower must be strictly less than upper')])
def test_interval_error_init(lower, upper, msg):
    with pytest.raises(ValueError, match=msg):
        Interval(int, lower=lower, upper=upper)


@pytest.mark.parametrize('interval, value', [
    (Interval(int, lower=None, upper=2), 1),
    (Interval(int, lower=None, upper=2), 2),
    (Interval(int, lower=-3, upper=None), 3),
    (Interval(int, lower=-3, upper=None), -3),
    (Interval(int, lower=-3, upper=2), 0),
    (Interval(int, lower=-3, upper=2), -3),
    (Interval(int, lower=-3, upper=2), 2),
    (Interval(float, lower=None, upper=2), 1.0),
    (Interval(float, lower=None, upper=2), 2.0),
    (Interval(float, lower=-3, upper=None), 3.0),
    (Interval(float, lower=-3, upper=None), -3.0),
    (Interval(float, lower=-3, upper=2), 0.0),
    (Interval(float, lower=-3, upper=2), -3.0),
    (Interval(float, lower=-3, upper=2), 2.0),
])
def test_interval_valid_values(interval, value):
    interval.validate(value, "tol")


@pytest.mark.parametrize('interval, value, msg', [
    (Interval(int, lower=None, upper=2), 1.0, 'tol: 1.0 is not a int'),
    (Interval(float, lower=None, upper=2), 1, 'tol: 1 is not a float'),
])
def test_interval_invalid_type(interval, value, msg):
    with pytest.raises(TypeError, match=msg):
        interval.validate(value, "tol")


@pytest.mark.parametrize('interval, value, msg', [
    (Interval(int, lower=None, upper=2), 3, r'3 not in \(-inf, 2\]'),
    (Interval(int, lower=None, upper=2,
              upper_inclusive=False), 2, r'2 not in \(-inf, 2\)'),
    (Interval(int, lower=-3, upper=None), -4, r'-4 not in \[-3, inf\)'),
    (Interval(int, lower=-3, upper=None,
              lower_inclusive=False), -3, r'-3 not in \(-3, inf\)'),
    (Interval(int, lower=-3, upper=2), 3, r'3 not in \[-3, 2\]'),
    (Interval(int, lower=-3, upper=2), -4, r'-4 not in \[-3, 2\]'),
    (Interval(int, lower=-3, upper=2,
              lower_inclusive=False), -3, r'-3 not in \(-3, 2\]'),
    (Interval(int, lower=-3, upper=2,
              upper_inclusive=False), 2, r'2 not in \[-3, 2\)'),
])
def test_interval_invalid_values(interval, value, msg):
    with pytest.raises(ValueError, match=msg):
        interval.validate(value, 'tol')
