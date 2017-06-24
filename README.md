# Dynamight 💣💪

*Dynamic Strong Typing in Python*

A quick and dirty use of [Python function annotations](https://docs.python.org/3/tutorial/controlflow.html#function-annotations) to apply strong typing to functions and methods at runtime. If inputs or outputs of a function do not match the type specified in the function annotation, a type error will be thrown. This strong typing is applied to individual functions/classes through a decorator. As an example of usage:

```python
import dynamight

@dynamight.strong
def is_able_to_pass(name : str, quest : str, favourite_colour : str) -> bool:
    if name == "Lancelot" and quest == "seek the holy grail":
        followup_favourite_colour = input("...")
        if favourite_colour == followup_favourite_colour:
            return True
    return False

bridge_keepers_decision = is_able_to_pass("Lancelot", "Really likes bridges", 5)
# Will raise a TypeError when favourite_colour receives an int instead of a str
```

Dynamight can be installed through Pip:

```
pip install dynamight
```

### Key Features

This is something I whipped together fairly quickly to experiment with function annotations and didn't want to get too bogged down in; if you're looking for an actual solution for static typing in Python, you probably want [MyPy](http://mypy-lang.org/) at "compile" time or [Enforce](https://github.com/RussBaz/enforce) at runtime.

Despite this there are a few features of my approach I'm quite proud of:

* Strong typing on the output of generator functions (functions which `yield`). In a somewhat hacky way due to not being able to modify the generator returned by a generator function, the generator returned is replaced with a similar iterable class which tries to copy the original generator (but validates the output of `__next__()`).

* Flexible lists of possible types - being able to type a parameter as `[int, str]` as well as just `str`, so either a string or an integer value will be allowed.

### Notes on usage

This should sum up all the key things you need to know about supported function annotations and applying the decorator:

###### Order of decorators matters

```python
class SomeClass():

    @staticmethod
    @dynamight.strong
    def happy_function(name : str):
        # this ordering works correctly
        pass

    @dynamight.strong
    @staticmethod
    def sad_function(name : str):
        # this ordering will cause an exception when the module is initializing
        pass
```

##### Types in function annotations are covariant

*An instance of a subclass will be accepted as well as an instance of the class*

```python
@dynamight.strong
def some_function(anything : object):
    pass

# This wont throw a TypeError as str is a subclass of object
some_function("something")
```

##### Covers most basic types

*However currently specifying a type of item within a collection is not implemented*

```python
bool, str, int, list, dict, float, object, tuple, set, None
# also custom classes will work too
```

##### `None` is a special case

```python
@dynamight.strong
def some_function() -> None:
    pass

# None will be converted to type(None) behind the scenes, so use None.
```

##### Applying `strong` to a class affects all methods

*It's not going to have any effect on functions without annotations though*

```python
@dynamight.strong
class Hogwarts():

    # will be wrapped but has no effect
    def add_troll_to_dungeon(self, troll, dungeon):
        pass

    # will be wrapped and type checked when called
    def move_stairs_around(self, angle : int) -> None:
        pass
```

##### `strong` wont break `*args` and `**kwargs`

*Trying to apply typing to them is useless but it's not going to break your functions with them in*

##### `test_strong_type` is a good place to look for more usage examples

### Miscellaneous

Feedback appreciated! This was a project I worked on with an aim to see what I could get just done and released ASAP, rather than starting another programming project I don't get around to finishing.

A few other ideas I had for this but didn't have time for are:
* Using the `typing` library to check for collections of typed items as function annotations.
* Since strong typing doesn't seem as necessary in Python/isn't integral to the language, another idea I had was something like a wrapper which performs a conversion on inputs which don't match the type in the annotation, to the specified type, through some sort of graph of transforms. Would be a kind of defensive programming.
