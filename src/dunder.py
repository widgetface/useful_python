class Example:
    # class will have a fixed set of attributes
    # Much more eficient
    # Avoid using __slots__ if you need dynamic assignment of new attributes
    # or if the class is meant to be subclassed by unknown users' classes.
    # # __slots__ = ['name', 'score']

    def __new__(cls):
        print("Creating Instance called before __init__")
        return super(Example, cls).__new__(cls)


    def __init__(self):
        print("Initializing Instance")

    def __getattr__(self, name):
        if name == "secret":
            raise AttributeError("Access Denied")
        return self.__dict__.get(name, f"{name} not found")

    def __setattr__(self, name, value):
        if name == "secret":
            raise AttributeError("Cannot modify secret")
        self.__dict__[name] = value

    def __delattr__(self, name):
        if name == "secret":
            raise AttributeError("Cannot delete secret")
        del self.__dict__[name]

    def __call__(self):
        # Allows an instance of a class to be called as a function
        print("__call__")


e = Example()
print(e())
# You cannot get secret -> print(e.secret)


class Car:
    def __init__(self, make, model, year, max_speed):
        self.make = make
        self.model = model
        self.year = year
        self.max_speed = max_speed

    def display_info(self):
        return (
            f"{self.year} {self.make} {self.model} - Max Speed: {self.max_speed} km/h"
        )

    # @classmethod to create a SportsCar
    @classmethod
    def create_sports_car(cls, make, model, year):
        max_speed = 300  # Sports car typically has high speed
        return cls(make, model, year, max_speed)

    # @classmethod to create a FamilyCar
    @classmethod
    def create_family_car(cls, make, model, year):
        max_speed = 180  # Family cars usually have lower top speeds
        return cls(make, model, year, max_speed)


# Using the class methods to create cars
sports_car = Car.create_sports_car("Ferrari", "488", 2020)
family_car = Car.create_family_car("Toyota", "Camry", 2021)

# Display information
print(sports_car.display_info())  # Ferrari 488 - Max Speed: 300 km/h
print(family_car.display_info())  # Toyota Camry - Max Speed: 180 km/h
