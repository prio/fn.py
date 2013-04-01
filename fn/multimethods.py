from functools import wraps


# Threadsafe?
__mm_state = {}


#(derive ::rect ::shape)

class _MultiMethod(object):
    def __init__(self, name, dispatch_fn):
        self.name = name
        self._dispatch_fn = dispatch_fn
        self.dispatchs = {}

    def __call__(self, *args, **kwds):
        dispatch_on = self._dispatch_fn(*args, **kwds)
        function = self.dispatchs.get(dispatch_on)
        if function is None:
            function = self.dispatchs.get("default")
            if function is None:
                raise TypeError("no match")
        return function(*args, **kwds)

    def register(self, function, *values):
        if values in self.dispatchs:
            raise TypeError("duplicate registration")
        if len(values) == 1:
            values = values[0]
        self.dispatchs[values] = function


def multi(function):
    name = function.__name__
    mm = __mm_state[name] = _MultiMethod(name, function)    
    def init(*args, **kwds):
        return mm(*args, **kwds)
    return init


def method(*values):
    def call(function):
        name = function.__name__
        mm = __mm_state.get(name)
        if mm is None:
            raise TypeError("no matching multi function found")
        mm.register(function, *values)
        return mm
    return call


# Test
@multi 
def greeting(x): 
    return x["language"]
 
@method("English")
def greeting(params):
    return "Hello!"
 
@method("French")
def greeting(params):
    return "Bonjour!"

@method("default")
def greeting(params):
    raise ValueError("I don't know the {} language".format(params["language"]))


@multi
def add(x, y):
    return type(x)

@method(str)
def add(x, y):
    return " ".join((x, y))

@method(int)
def add(x, y):
    return x + y

@method("default")
def add(x, y):
    return x + y


@multi
def subtract(x, y):
    return (type(x), type(y))

@method(str, str)
def subtract(x, y):
    return x.replace(y, "").strip()

@method(str, int)
def subtract(x, y):
    return x[:-y]

@method("default")
def subtract(x, y):
    return x - y


import unittest


class TestMultiMethods(unittest.TestCase):
    def test_it_dispatches_using_value(self):
        english_map = {"id": "1", "language": "English"}
        french_map = {"id": "2", "language": "French"}
        spanish_map = {"id": "3", "language": "Spanish"} 
        self.assertEqual(greeting(english_map), "Hello!")
        self.assertEqual(greeting(french_map), "Bonjour!")
        try:
            greeting(spanish_map)
            self.fail("Should have failed")
        except ValueError:
            pass #Expected

    def test_it_dispatched_using_single_type(self):
        self.assertEqual(add("hi", "there"), "hi there")
        self.assertEqual(add(4, 5), 9)

    def test_it_dispatched_using_multiple_types(self):
        self.assertEqual(subtract(4, 5), -1)
        self.assertEqual(subtract("hi there", "there"), "hi")
        self.assertEqual(subtract("hi there", 6), "hi")


if __name__ == '__main__':
    unittest.main()