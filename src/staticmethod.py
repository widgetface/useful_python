# Organizational Benefit: You may want to group related functions under a class, even if those functions don't need access to instance-specific data. This can help with organization and structure, especially if you have a set of related functions that could conceptually belong to the class.
# Namespace: Static methods can also help avoid naming conflicts since they belong to the class namespace.
# Code clarity: It’s clear that the function is logically related to the class but doesn’t require an instance of it.

class TemperatureConverter:
    @staticmethod
    def celsius_to_fahrenheit(celsius):
        return (celsius * 9/5) + 32


# Usage
fahrenheit = TemperatureConverter.celsius_to_fahrenheit(0)
print(fahrenheit)  # Output: 32.0
