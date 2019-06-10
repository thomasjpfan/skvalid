from abc import ABC
from abc import abstractmethod

_DEFAULT_TAG = ['tune']


class Parameter(ABC):
    def __init__(self, tags=None):
        if tags is None:
            tags = _DEFAULT_TAG
        self.tags = tags

    @abstractmethod
    def validate(self, value):
        ...


class Const(Parameter):
    def __init__(self, value, tags=None):
        super().__init__(tags=tags)
        self.value = value

    def validate(self, value):
        if value != self.value:
            raise ValueError("{} != {}".format(value, self.value))


class TypeOf(Parameter):
    def __init__(self, *types, tags=None):
        super().__init__(tags=tags)
        self.types = types

    def validate(self, value):
        for t in self.types:
            if isinstance(value, t):
                return

        if len(self.types) == 1:
            raise TypeError("{} is not a {}".format(value,
                                                    self.types[0].__name__))
        type_names = [t.__name__ for t in self.types]
        raise TypeError("{} is not a {}".format(value,
                                                " or ".join(type_names)))


class Enum(Parameter):
    def __init__(self, *members, tags=None):
        super().__init__(tags=tags)
        if len(members) == 0:
            raise ValueError("members must have at least one item")
        self.members = members

    def validate(self, value):
        if value not in self.members:
            members_str = ', '.join(str(m) for m in self.members)
            raise ValueError("{} is not in [{}]".format(value, members_str))


class Union(Parameter):
    def __init__(self, *params, tags=None):
        if len(params) == 0:
            raise ValueError("parameters must have at least one item")
        for p in params:
            if not isinstance(p, Parameter):
                raise ValueError("all parameters must be of type Parameter")
            p.tags = []
        super().__init__(tags=tags)
        self.params = params

    def validate(self, value):
        error_msg = []
        for p in self.params:
            try:
                p.validate(value)
                return
            except (TypeError, ValueError) as e:
                error_msg.append(str(e))

        # None of the params validated value
        raise ValueError(', '.join(error_msg))


class Interval(TypeOf):
    def __init__(self,
                 typ,
                 lower=None,
                 upper=None,
                 lower_inclusive=True,
                 upper_inclusive=True,
                 tags=None):
        if lower is None and upper is None:
            raise ValueError("lower or upper must be defined")
        if None not in (lower, upper) and lower >= upper:
            raise ValueError("lower must be strictly less than upper")

        super().__init__(typ, tags=tags)
        self.lower = lower
        self.upper = upper
        self.lower_inclusive = lower_inclusive
        self.upper_inclusive = upper_inclusive

    def validate(self, value):
        super().validate(value)

        if self.lower is not None:
            if self.lower_inclusive:
                lower_in_range = self.lower <= value
            else:
                lower_in_range = self.lower < value
            if not lower_in_range:
                raise ValueError(self._get_error_msg(value))

        if self.upper is not None:
            if self.upper_inclusive:
                upper_in_range = value <= self.upper
            else:
                upper_in_range = value < self.upper
            if not upper_in_range:
                raise ValueError(self._get_error_msg(value))

    def _get_error_msg(self, value):
        msg_list = ["{} not in".format(value)]
        if self.lower is not None:
            if self.lower_inclusive:
                lower_str = "[{},".format(self.lower)
            else:
                lower_str = "({},".format(self.lower)
            msg_list.append(lower_str)
        else:
            msg_list.append("(-inf,")

        if self.upper is not None:
            if self.upper_inclusive:
                upper_str = "{}]".format(self.upper)
            else:
                upper_str = "{})".format(self.upper)
            msg_list.append(upper_str)
        else:
            msg_list.append("inf)")
        return " ".join(msg_list)
