# Decorator, Context Manager, Generator

import functools
import time
from contextlib import contextmanager

def logger(func):
    """Logs every function call."""
    @functools.wraps(func)   # Preserves the name and docstring of the function.
    def wrapper(*args, **kwargs):   # *args: positional arguments, **kwargs: keyword arguments
        print(f"[LOG] {func.__name__} logging started.")
        result = func(*args, **kwargs)
        print(f"[LOG] {func.__name__} completed.")
        return result
    return wrapper

def timer(func):
    """Measures the function's execution time."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"[TIME] {func.__name__}: {elapsed:.4f}s")
        return result
    return wrapper

def validate_patient(func):
    """Validates patient data before the function runs."""
    @functools.wraps(func)
    def wrapper(patient, *args, **kwargs):
        if not patient.name.strip():
            raise ValueError("Patient name cannot be empty.")
        if not (0 < patient.age < 150):
            raise ValueError(f"Invalid age: {patient.age}")
        return func(patient, *args, **kwargs)
    return wrapper

def require_records(func):
    """Raises an error if no patient record exists (uses bool)."""
    @functools.wraps(func)
    def wrapper(patient, *args, **kwargs):
        if not patient:    # Patient.__bool__: Returns True if the record exists.
            raise ValueError(f"{patient.name} no record found for the forensic patient.")
        return func(patient, *args, **kwargs)
    return wrapper

@contextmanager   # Converts the generator into a context manager.
def patient_file(filepath, mode="r"):
    """Safely opens and closes the patient file."""
    f = None
    try:
        print(f"[FILE] Opening...: {filepath}")
        f = open(filepath, mode, encoding="utf-8")
        yield f   # __enter__ before yield, __exit__ after
    except FileNotFoundError:
        print(f"[FILE] {filepath} Not found.")
        yield None
    finally:
        if f:
            f.close()
            print(f"[FILE] Closed: {filepath}")

class DataTransaction:
    """Safely manages data operations — rolls back on error."""

    def __init__(self, data_store):
        self.data_store = data_store
        self.backup = None

    def __enter__(self):  # Runs when the with block starts.
        self.backup = self.data_store.copy()
        print("[TX] Operation started.")
        return self.data_store
    
    def __exit__(self, exc_type, exc, tb):  # Runs when the with block ends.
        if exc_type:
            self.data_store.clear()
            self.data_store.update(self.backup)  # Geri al
            print(f"[TX] Rolled back: {exc}")
            return True   # True: suppresses the error and lets the program continue
        print("[TX] approved.")
        return False   # False: does not suppress the error
    
def generate_report(patients):
    """Generates the report line by line — doesn't load everything into memory."""
    yield "=" * 55
    yield "           🏥 PATIENT REPORT"
    yield "=" * 55
    for i, p in enumerate(patients, 1):
        yield f"\n{i}. {p}"   # Patient.__str__
        yield f"   Age: {p.age} | Weight: {p.weight}kg | Height: {p._height}cm"
        yield f"   Record count: {len(p)}"   # Patient.__len__
        if p.medications:
            yield f"   Medications: {', '.join(p.medications)}"
    yield "\n" + "=" * 55
    yield f"Total: {len(patients)} patient"

def filter_high_risk(patients):
    """Only yields high-risk patients."""
    for p in patients:
        if p.bmi >= 30 or p.bmi < 18.5:
            yield p

def paginate(items, page_size=3):
    """Paginates the list."""
    for i in range(0, len(items), page_size):
        yield items[i:i + page_size]

def process_pipeline(patients, min_age=0, max_bmi=float("inf")):
    """Generator pipeline: chained filters"""
    def age_filter(pts):
        for p in pts:
            if p.age >= min_age:
                yield p

    def bmi_filter(pts):
        for p in pts:
            if p.bmi <= max_bmi:
                yield p

    yield from bmi_filter(age_filter(patients))