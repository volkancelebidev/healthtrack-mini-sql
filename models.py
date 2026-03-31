# Classes, Inheritance, super(), @property, @classmethod, @staticmethod, Magic Methods

from datetime import datetime

class Person:
    def __init__(self, name, age, id_number):
        self.name = name
        self._age = age   # Do not access directly from outside '_' use the property.
        self.id_number = id_number

    @property
    def age(self):
        return self._age
    
    @age.setter
    def age(self, value):
        if value < 0 or value > 150:
            raise ValueError(f"Invalid age: {value}")
        self._age = value

    def __str__(self):
        return f"{self.name}  (ID: {self.id_number})"
    
    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}', age={self._age})"
    
class Patient(Person):
    def __init__(self, name, age, id_number, weight, height):
        super().__init__(name, age, id_number)
        self._weight = weight
        self._height = height
        self.records = []  # Medical notes
        self.medications = []

    @property
    def bmi(self):    # Computed property: read-only from outside
        height_m = self._height / 100
        return round(self._weight / (height_m ** 2), 1)
    
    @property
    def bmi_category(self):
        if self.bmi < 18.5:
            return "Underweight"
        elif self.bmi < 25:
            return "Normal"
        elif self.bmi < 30:
            return "Overweight"
        else:
            return "Obese"
        
    @property
    def weight(self):
        return self._weight
    
    @weight.setter
    def weight(self, value):
        if value <= 0:
            raise ValueError("Weight must be positive")
        self._weight = value

    def add_record(self, note):
        self.records.append({
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "note": note
        })

    def add_medication(self, med):
        self.medications.append(med)

    @classmethod  # Factory method that creates a Patient from a dictionary
    def from_dict(cls, data):
        p = cls(data["name"], data["age"], data["id_number"],
                data["weight"], data["height"])
        p.records = data.get("records", [])
        p.medications = data.get("medications", [])
        return p
    
    @staticmethod  # Helper method that doesn't require an instance
    def calculate_bmi(weight, height):
        return round(weight / (height / 100) ** 2, 1)
    
    def to_dict(self):
        return {
            "name": self.name, "age": self._age,
            "id_number": self.id_number,
            "weight": self._weight, "height": self._height,
            "records": self.records, "medications": self.medications
        }
    
    def __str__(self):
        return f"Patient: {self.name} | BMI: {self.bmi} ({self.bmi_category})"
    
    def __repr__(self):
        return f"Patient(name='{self.name}', age={self._age}, bmi={self.bmi})"
    
    def __len__(self):   # len(patient): record count
        return len(self.records)
    
    def __bool__(self):  # if patient: → True if the record exists
        return len(self.records) > 0
    
    def __eq__(self, other):   # ID comparison
        return self.id_number == other.id_number
    
    def __lt__(self, other):   # Sorting by age
        return self._age < other._age
    
    def __gt__(self, other): 
        return self._age > other._age
    
class EmergencyPatient(Patient):
    PRIORITY_LEVELS = ["low", "medium", "high", "critical"]

    def __init__(self, name, age, id_number, weight, height, priority, condition):
        super().__init__(name, age, id_number, weight, height)
        self.priority = priority
        self.condition = condition
        self.arrival_time = datetime.now().strftime("%Y-%m-%d %H:%M")

    def __str__(self):  # Overrides the parent's __str__
        return f"EMERGENCY: {self.name} | Priority: {self.priority.upper()} | {self.condition}"
    
    def __gt__(self, other):
        if isinstance(other, EmergencyPatient):
            return (self.PRIORITY_LEVELS.index(self.priority) >
                    self.PRIORITY_LEVELS.index(other.priority))
        return super().__gt__(other)
    
class Doctor(Person):
    _doctor_count = 0   # Class variable: shared among all instances

    def __init__(self, name, age, id_number, specialty, license_number):
        super().__init__(name, age, id_number)
        self.specialty = specialty
        self.license_number = license_number
        self.patients = []
        Doctor._doctor_count += 1

    def assign_patient(self, patient):
        self.patients.append(patient)

    @classmethod   
    def get_doctor_count(cls): # Called on the class
        return cls._doctor_count
    
    @staticmethod
    def validate_license(license_number):   # No instance required
        return len(license_number) == 8 and license_number.isalnum()
    
    def __str__(self):
        return f"Dr. {self.name} | {self.specialty} | Patient: {len(self.patients)}"
    
    def __repr__(self):
        return f"Doctor(name='{self.name}', specialty='{self.specialty}')"
    
class PatientQueue:
    def __init__(self):
        self.queue = []
        self._index = 0

    def add(self, patient):
        self.queue.append(patient)

    def __iter__(self):   # Called by for loops — returns self
        self._index = 0
        return self
    
    def __next__(self):   # Returns the next patient on each step
        if self._index >= len(self.queue):
            raise StopIteration   # "Finished" signal
        patient = self.queue[self._index]
        self._index += 1
        return patient
    
    def __len__(self):
        return len(self.queue)
    
    def __contains__(self, patient):  # x in queue
        return patient in self.queue
    
    def __str__(self):
        return f"Queue: {len(self)} patient"
    

    

    
    


    