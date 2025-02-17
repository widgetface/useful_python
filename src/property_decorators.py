class Temperature:
    def __init__(self, celsius):
        self._celsius = celsius

    @property
    def celsius(self):
        return self._celsius
      
    @celsius.setter
    def celsius(self, value):
        if value < -273.15:
            raise ValueError("Temperature below absolute zero!")
        self._celsius = value

    @celsius.deleter
    def celsius(self):
        print("Deleting celsius")
        del self._celsius

# Usage
temp = Temperature(100)
print(temp.celsius)  # 100
temp.celsius = -300  # Raises ValueError
del temp.celsius  # "Deleting celsius"
