class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        pass  # Defined as pass for now

class Dog(Animal):  # Inherits from Animal
    def speak(self):
        return "Woof!"
    
doggo = Dog()
print(doggo.speak)