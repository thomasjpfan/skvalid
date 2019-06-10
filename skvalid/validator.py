from itertools import chain


def validate_paramters(config, **params):
    # check parameters exist
    for name in params:
        if name not in config:
            raise KeyError("{} is not a valid parameter".format(name))

    # validate parameters
    for param, value in params.items():
        config[param].validate(value)

    # validate conditions
    try:
        conditions = config["_conditions"]
    except KeyError:
        # ignore with there are no conditions
        return

    for key, groups in conditions.items():
        # ignore if value not in params
        try:
            value = params[key]
            allowed_choices = set(groups[value])
            all_choices = set(chain.from_iterable(groups.values()))
            bad_choices = sorted(all_choices - allowed_choices)
            for bad_choice in bad_choices:
                bad_choice_value = params.get(bad_choice)
                if bad_choice_value is not None:
                    raise ValueError("{}: {}, not compatible with {}".format(
                        key, value, bad_choice))
        except KeyError:
            continue
