import functools
import inspect
import types


def strong(entity):
    """Decorator which applies strong typing using function annotations."""

    if inspect.isgeneratorfunction(entity):
        return create_generator_function_wrapper(entity)
    elif inspect.isfunction(entity) or inspect.ismethod(entity):
        return create_function_or_method_wrapper(entity)
    elif inspect.isclass(entity):
        return create_wrappers_for_class_methods(entity)
    else:
        raise Exception("Unsupported Object to apply strong typing to")


def create_generator_function_wrapper(generator_func):
    """Wraps a generator function to check inputs and outputs.

       The generator function which returns a generator is trivial to check.
       Since the generator built-in cannot be modified, it instead creates
       a generator copy which implements whatever the returned generator's
       next method would do, but checks the return is of the type specified
       on the *original* generator function annotation.
    """

    @functools.wraps(generator_func)
    def generator_function_wrapper(*args, **kwargs):

        param_names = generator_func.__code__.co_varnames[: generator_func.__code__.co_argcount]
        param_types = generator_func.__annotations__
        for name, p_types in param_types.items():
            if type(p_types) == list:
                param_types[name] = tuple(p_types)
            if p_types is None:
                param_types[name] = type(None)

        for param, arg in zip(param_names, args):
            if param in param_types and not isinstance(arg, param_types[param]):
                raise TypeError("Expected {0} but received {1}".format(param_types[param], type(arg)))

        returned_generator = generator_func(*args, **kwargs)

        if not isinstance(returned_generator, types.GeneratorType):
            raise TypeError("Expected to receive a generator object but got something else")

        if "return" in param_types:

            class GeneratorCopy(object):

                def __iter__(self):
                    return self

                def __next__(self):
                    result = returned_generator.__next__()
                    if not isinstance(result, param_types["return"]):
                        raise TypeError(
                            "Expected {0} but received {1}".format(param_types["return"], type(result)))
                    return result

            overridden_generator = GeneratorCopy()
            return overridden_generator

        return returned_generator

    return generator_function_wrapper


def create_function_or_method_wrapper(func):
    """Wraps a function, or a class method."""

    @functools.wraps(func)
    def function_wrapper(*args, **kwargs):
        """Wrapper which checks input and output against function annotations first."""
        param_names = func.__code__.co_varnames[: func.__code__.co_argcount]
        param_types = func.__annotations__
        # TODO could be using sig.bind, inspect.signature/parameters as a better implementation
        # would allow this to be extended to args/kwargs checking

        for name, p_types in param_types.items():
            if type(p_types) == list:
                param_types[name] = tuple(p_types)
            if p_types is None:
                param_types[name] = type(None)

        for param, arg in zip(param_names, args):
            if param in param_types and not isinstance(arg, param_types[param]):
                raise TypeError("Expected {0} but received {1}".format(param_types[param], type(arg)))

        result = func(*args, **kwargs)

        if "return" in param_types and not isinstance(result, param_types["return"]):
            raise TypeError("Expected {0} but received {1}".format(param_types["return"], type(result)))

        return result

    return function_wrapper


def create_wrappers_for_class_methods(klass):
    """Wraps all the functions and class methods of a class."""

    for name, func in inspect.getmembers(klass, predicate=inspect.isfunction):
        setattr(klass, name, strong(func))
    return klass
