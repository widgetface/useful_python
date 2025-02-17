# The __call__ method in Python allows an instance of a class to be called
# like a function. By implementing this method in a class,
#  you make it possible to invoke an instance directly as
#  if it were a function. This can be a powerful and
#  useful feature when designing classes that need to
#  behave like functions but still encapsulate state or
#  other methods.

# Here are some scenarios where using the __call__ method
# can be beneficial:

### 1. **Simulating Function Objects (Callable Objects)**

# A common use case for `__call__` is when you want an object to behave like a function. This can be useful if you want to store some state in an object and need to apply some computation when the object is "called."

class Adder:
    def __init__(self, initial_value=0):
        self.total = initial_value

    def __call__(self, value):
        self.total += value
        return self.total


# Using the class as a callable
adder = Adder(5)
print(adder(10))  # 15 (5 + 10)
print(adder(20))  # 35 (15 + 20)


# **Why use `__call__` here?**
# - The `Adder` class behaves like a function that keeps a running total, making it easy to add values to it.
# - It encapsulates the `total` state and allows us to update it each time the object is called, providing a cleaner and more readable way of using the object.



### 2. **Stateful Function Objects (Memorization or Caching)**

# You can use `__call__` to create a stateful function object, such as a memoizer or cache that stores previous function results to optimize repeated computations.

class Memoizer:
    def __init__(self, function):
        self.function = function
        self.cache = {}

    def __call__(self, *args):
        if args not in self.cache:
            print(f"Computing {args}...")
            self.cache[args] = self.function(*args)
        else:
            print(f"Fetching from cache: {args}")
        return self.cache[args]


# Using the memoizer
def slow_function(x):
    return x * 2  # Simulate a slow function

memoized_function = Memoizer(slow_function)

# The first call computes the value
print(memoized_function(5))  # Computing (5), result: 10

# The second call fetches from cache
print(memoized_function(5))  # Fetching from cache, result: 10


# **Why use `__call__` here?**
# - The `Memoizer` class wraps the `slow_function` and caches its results to avoid re-computation for the same inputs.
# - By making `Memoizer` callable, you can use the same syntax as calling a regular function, keeping the code concise and clean.

### 3. **Customizable Behaviors for Function Calls**

# You can use `__call__` to implement more flexible and dynamic behaviors in your objects, such as adjusting how arguments are passed or how the function is executed.


class Multiplier:
    def __init__(self, factor):
        self.factor = factor

    def __call__(self, value):
        return value * self.factor


# Using the multiplier
double = Multiplier(2)
triple = Multiplier(3)

print(double(5))  # 10 (5 * 2)
print(triple(5))  # 15 (5 * 3)


# **Why use `__call__` here?**
# - The `Multiplier` class is designed to adjust a value by a specific factor.
# - Instead of writing a separate method, you can call the instance directly with values to get the result, making the code more intuitive.



### 4. **Function Composition**

# Using `__call__`, you can combine multiple callable objects to compose complex behavior.

class FunctionChain:
    def __init__(self, *functions):
        self.functions = functions

    def __call__(self, value):
        for function in self.functions:
            value = function(value)
        return value


# Define some simple functions
def add_two(x):
    return x + 2

def multiply_by_three(x):
    return x * 3

# Create a function chain
chain = FunctionChain(add_two, multiply_by_three)

print(chain(5))  # (5 + 2) * 3 = 21


# **Why use `__call__` here?**
# - The `FunctionChain` class allows you to chain multiple functions together.
# - Instead of manually calling each function, you can simply call the object with an argument, and it will process the argument through all the functions in the chain, keeping the code concise.



### 5. **Event Handling or Callbacks**

# You can use `__call__` to define objects that act as event handlers or callbacks, where calling the object triggers an action.


class EventHandler:
    def __init__(self, event_name):
        self.event_name = event_name

    def __call__(self, *args, **kwargs):
        print(f"Event '{self.event_name}' triggered with args: {args} and kwargs: {kwargs}")


# Simulate triggering an event
click_event = EventHandler("click")
click_event(10, 20, button="left")

keypress_event = EventHandler("keypress")
keypress_event("a", "b", modifier="shift")


# **Why use `__call__` here?**
# - The `EventHandler` object acts as a generic event handler.
# - Instead of defining methods for each type of event, the object can be called directly with parameters, making the event handling process more flexible.

### Summary of when to use `__call__`:

# - **Function-like behavior**: When you want an object to behave like a function.
# - **Stateful function objects**: When you need to store state or cache results, such as in memoization.
# - **Dynamic behaviors**: When the behavior of an object should change based on its state or input values.
# - **Composition**: When you want to compose a series of operations into a single callable object.
# - **Event handling or callbacks**: When you want to define objects that handle events or execute callbacks dynamically.

# In general, `__call__` makes your objects more flexible, allowing them to be used in ways that resemble function calls.
