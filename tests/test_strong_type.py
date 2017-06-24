import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'dynamight')))
import dynamight


# ----------------------------
# LARGER BATCH OF SIMPLE TESTS
# ----------------------------
# collection of functions with simple signatures

@dynamight.strong
def string_in_none_out(var1: str) -> None: pass


@dynamight.strong
def int_in_none_out(var1: int) -> None: pass


@dynamight.strong
def list_in_none_out(var1: list) -> None: pass


@dynamight.strong
def float_in_none_out(var1: float) -> None: pass


@dynamight.strong
def bool_in_none_out(var1: bool) -> None: pass


@dynamight.strong
def string_in_any_out(var1: str): return int(var1)


@dynamight.strong
def any_in_string_out(var1) -> str: return var1


@dynamight.strong
def any_in_tuple_out(var1) -> tuple: return var1


@dynamight.strong
def none_in_dict_out(var1: None) -> dict: return {}


@dynamight.strong
def variety_in_any_out(var1: str, var2: list, var3: dict): pass


@dynamight.strong
def str_in_with_default(var1: str = "default"): pass


@dynamight.strong
def str_or_int_in_any_out(var1: [str, int]): pass


@dynamight.strong
def list_or_dict_in_any_out(var1: (list, dict)): pass


class DummyClass:
    @classmethod
    @dynamight.strong
    def strong_typed_class_method(cls, name: str):
        pass

    @staticmethod
    @dynamight.strong
    def strong_typed_static_method(some_number: int):
        pass

    @dynamight.strong
    def strong_typed_object_method(self, words: list):
        pass


@dynamight.strong
class AnotherDummyClass:
    def strong_typed_at_class_level_object_method(self, name: str):
        pass

    def another_strong_typed_at_class_level_object_method(self, age: int) -> int:
        return 5

    @staticmethod
    def another_strong_typed_static_method(some_number: int):
        pass

    @classmethod
    def another_strong_typed_class_method(some_number: int):
        pass


dummyClass = DummyClass()
anotherDummyClass = AnotherDummyClass()

# test cases for simple functions in the form (function, succeeding test case args, failing test case args)
simple_functions = [
    # one in, none outs
    (string_in_none_out, ["hello"], [1337]),
    (string_in_none_out, [r"hi there"], [None]),
    (int_in_none_out, [123], ["sun"]),
    (list_in_none_out, [["a", "b"]], [{}]),
    (float_in_none_out, [float(5)], [5]),
    (bool_in_none_out, [False], [None]),
    # one in, any outs
    (string_in_any_out, ["123"], [1337]),
    # any in, one outs
    (any_in_string_out, ["hi"], [123]),
    (any_in_tuple_out, [(1, 2, 3)], [[1, 2, 3]]),
    # none in, one outs
    (none_in_dict_out, [None], ["something"]),
    # many in, one outs
    (variety_in_any_out, ["", [], {}], ["", 5, ()]),
    # with defaults
    (str_in_with_default, [], [5]),
    (str_in_with_default, ["test"], [None]),
    # with multiple types specified
    (str_or_int_in_any_out, ["test"], [(1, 2)]),
    (str_or_int_in_any_out, [123], [float(123)]),
    (list_or_dict_in_any_out, [[]], [()]),
    (list_or_dict_in_any_out, [{"hello": "world"}], [456]),

    (DummyClass.strong_typed_class_method, ["hello"], [123]),
    (dummyClass.strong_typed_object_method, [["one", "two"]], ["one"]),

    (DummyClass.strong_typed_static_method, [5], ["five"]),

    (anotherDummyClass.strong_typed_at_class_level_object_method, ["hi"], [5]),
    (anotherDummyClass.another_strong_typed_at_class_level_object_method, [5], ["oh"])
]


@pytest.fixture(params=simple_functions)
def function_and_arg_lists(request):
    yield request.param


def test_strong_typed_with_correct_params_succeeds(function_and_arg_lists):
    func, success_args, fail_args = function_and_arg_lists
    func(*success_args)


def test_strong_typed_with_incorrect_params_fails(function_and_arg_lists):
    func, success_args, fail_args = function_and_arg_lists
    with pytest.raises(TypeError):
        func(*fail_args)


# -------------------------
# OTHER MORE SPECIFIC TESTS
# -------------------------

def test_demonstrate_class_annotations_first_cause_exceptions():
    with pytest.raises(Exception):
        class FailingDummyClass:
            @dynamight.strong
            @classmethod
            def strong_typed_class_method(cls, name: str):
                pass


def test_demonstrate_static_annotations_first_cause_exceptions():
    with pytest.raises(Exception):
        class FailingDummyClass:
            @dynamight.strong
            @staticmethod
            def strong_typed_static_method(some_number: int):
                pass


@pytest.fixture
def func():
    def f() -> None: pass

    return f


def test_strong_type_preserves_function_info(func):
    original_name = func.__name__
    wrapped_func = dynamight.strong(func)
    assert (wrapped_func.__name__ == original_name)


def test_generator_failure_due_to_output_type():
    @dynamight.strong
    def wrapped_generator() -> int:
        for i in range(5):
            if i == 4:
                yield str(i)
            else:
                yield i

    with pytest.raises(TypeError):
        for j in wrapped_generator():
            pass


def test_kwargs_work_correctly():
    @dynamight.strong
    def dummy(var1: str, **kwargs) -> str: return kwargs["test"]

    result = dummy("", **{"test": "testing"})
    assert (result == "testing")
