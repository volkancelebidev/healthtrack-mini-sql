import sqlite3        # Built-in Python SQL library, no installation required
import json           # Reading and writing JSON files
from datetime import datetime   # Date and time operations
import functools      # Required for decorator implementation
from models import Patient      # Patient class from HealthTrack project


# ═══════════════════════════════════════════════════════
# DECORATOR
# ═══════════════════════════════════════════════════════

def logger(func):
    """
    Decorator that logs function calls.
    Prints function name when it starts and completes.
    """
    @functools.wraps(func)      # Preserves the original function's name and docstring
    def wrapper(*args, **kwargs):
        print(f"[LOG] {func.__name__} started")
        result = func(*args, **kwargs)  # Execute the actual function
        print(f"[LOG] {func.__name__} completed")
        return result           # Return the function's result
    return wrapper              # Return wrapper, don't call it


# ═══════════════════════════════════════════════════════
# DATABASE SETUP
# ═══════════════════════════════════════════════════════

def setup_database(db_name):
    """
    Creates the database tables if they don't exist.
    Tables: patients, medical_records, medications
    """
    with sqlite3.connect(db_name) as conn:  # Auto-closes connection when done
        # Patient information table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id         TEXT PRIMARY KEY,        -- Unique identifier, cannot repeat
                name       TEXT NOT NULL,           -- Cannot be empty
                age        INTEGER,                 -- Whole number
                weight     REAL,                    -- Decimal number (kg)
                height     REAL,                    -- Decimal number (cm)
                blood_type TEXT DEFAULT 'Unknown'   -- Default value if not provided
            )
        """)

        # Medical records table - linked to patients
        conn.execute("""
            CREATE TABLE IF NOT EXISTS medical_records (
                record_id  INTEGER PRIMARY KEY AUTOINCREMENT,  -- Auto-increments: 1, 2, 3...
                patient_id TEXT,                               -- Which patient this belongs to
                date       TEXT,                               -- Record date
                note       TEXT,                               -- Medical note
                FOREIGN KEY (patient_id) REFERENCES patients(id)  -- Links to patients table
            )
        """)

        # Medications table - linked to patients
        conn.execute("""
            CREATE TABLE IF NOT EXISTS medications (
                med_id     INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT,
                name       TEXT,
                FOREIGN KEY (patient_id) REFERENCES patients(id)
            )
        """)

        print("✅ Database tables ready")


# ═══════════════════════════════════════════════════════
# PATIENT OPERATIONS
# ═══════════════════════════════════════════════════════

@logger  # Automatically logs every call to this function
def save_patient(db_name, patient):
    """
    Saves a Patient object to the database.
    Includes medical records and medications.
    """
    with sqlite3.connect(db_name) as conn:
        # Save basic patient information
        conn.execute("""
            INSERT OR REPLACE INTO patients
            (id, name, age, weight, height)
            VALUES (?, ?, ?, ?, ?)          -- ? prevents SQL injection
        """, (patient.id_number, patient.name, patient.age,
              patient.weight, patient._height))

        # Save each medical record
        for r in patient.records:          # Iterates through each record dict
            conn.execute("""
                INSERT INTO medical_records (patient_id, date, note)
                VALUES (?, ?, ?)
            """, (patient.id_number, r["date"], r["note"]))

        # Save each medication
        for med in patient.medications:    # Iterates through each medication string
            conn.execute("""
                INSERT INTO medications (patient_id, name)
                VALUES (?, ?)
            """, (patient.id_number, med))


def load_patient(db_name, patient_id):
    """
    Loads a Patient object from the database.
    Includes medical records and medications.
    Returns None if patient not found.
    """
    with sqlite3.connect(db_name) as conn:
        # Fetch basic patient data
        row = conn.execute(
            "SELECT * FROM patients WHERE id = ?",
            (patient_id,)               # Trailing comma makes it a tuple
        ).fetchone()                    # Returns single row or None

        if not row:                     # Patient not found
            return None

        # Build Patient object from database row
        # row[0]=id, row[1]=name, row[2]=age, row[3]=weight, row[4]=height
        patient = Patient(row[1], row[2], row[0], row[3], row[4])

        # Load medical records
        records = conn.execute("""
            SELECT date, note FROM medical_records
            WHERE patient_id = ?
            ORDER BY date DESC          -- Most recent record first
        """, (patient_id,)).fetchall()

        for date, note in records:      # Unpack each tuple into date and note
            patient.records.append({"date": date, "note": note})

        # Load medications
        meds = conn.execute("""
            SELECT name FROM medications WHERE patient_id = ?
        """, (patient_id,)).fetchall()

        patient.medications = [m[0] for m in meds]  # Extract name from each tuple

        return patient


# ═══════════════════════════════════════════════════════
# QUERIES
# ═══════════════════════════════════════════════════════

def get_all_patients(db_name):
    """Returns all patients ordered by age (youngest first)."""
    with sqlite3.connect(db_name) as conn:
        return conn.execute("""
            SELECT * FROM patients
            ORDER BY age ASC            -- ASC: smallest to largest
        """).fetchall()


def get_high_risk(db_name):
    """
    Returns patients with BMI >= 30 (Obese) or BMI < 18.5 (Underweight).
    BMI is calculated directly in SQL.
    """
    with sqlite3.connect(db_name) as conn:
        return conn.execute("""
            SELECT name, age,
                ROUND(
                    weight / ((height/100) * (height/100)), 1
                ) as bmi                -- Calculate BMI, round to 1 decimal
            FROM patients
            WHERE
                weight / ((height/100) * (height/100)) >= 30   -- Obese
                OR
                weight / ((height/100) * (height/100)) < 18.5  -- Underweight
            ORDER BY bmi DESC           -- Highest BMI first
        """).fetchall()


def get_patients_by_age(db_name, min_age, max_age):
    """Returns patients within the given age range (inclusive)."""
    with sqlite3.connect(db_name) as conn:
        return conn.execute("""
            SELECT * FROM patients
            WHERE age BETWEEN ? AND ?   -- Includes both min and max values
            ORDER BY age
        """, (min_age, max_age)).fetchall()


# ═══════════════════════════════════════════════════════
# STATISTICS
# ═══════════════════════════════════════════════════════

@logger
def get_statistics(db_name):
    """
    Generates a full statistical report.
    Returns: general stats, BMI distribution, record counts per patient.
    """
    with sqlite3.connect(db_name) as conn:
        # General statistics - all in one query
        row = conn.execute("""
            SELECT
                COUNT(*)  as total,     -- Total number of patients
                MIN(age)  as min_age,   -- Youngest patient
                MAX(age)  as max_age,   -- Oldest patient
                AVG(age)  as avg_age    -- Average age
            FROM patients
        """).fetchone()

        stats = {
            "total"  : row[0],
            "min_age": row[1],
            "max_age": row[2],
            "avg_age": round(row[3], 1) if row[3] else 0  # AVG returns None if table is empty
        }

        # BMI distribution by category
        bmi_groups = conn.execute("""
            SELECT
                CASE                    -- SQL equivalent of if/elif
                    WHEN weight/((height/100)*(height/100)) < 18.5
                        THEN 'Underweight'
                    WHEN weight/((height/100)*(height/100)) < 25
                        THEN 'Normal'
                    WHEN weight/((height/100)*(height/100)) < 30
                        THEN 'Overweight'
                    ELSE 'Obese'
                END as category,
                COUNT(*) as count
            FROM patients
            GROUP BY category           -- Group patients by BMI category
            ORDER BY count DESC         -- Most common category first
        """).fetchall()

        # Record count per patient using JOIN
        patient_records = conn.execute("""
            SELECT p.name, COUNT(r.record_id) as record_count
            FROM patients p
            LEFT JOIN medical_records r     -- Includes patients with no records
            ON p.id = r.patient_id          -- Join condition
            GROUP BY p.id                   -- One row per patient
            ORDER BY record_count DESC      -- Most records first
        """).fetchall()

        return stats, bmi_groups, patient_records


# ═══════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════

def export_to_json(db_name, output_file):
    """Exports all patient data to a JSON file."""
    with sqlite3.connect(db_name) as conn:
        conn.row_factory = sqlite3.Row  # Allows dict-style access to rows
        data = [dict(row) for row in
                conn.execute("SELECT * FROM patients").fetchall()]
        # Converts each Row object to a Python dict

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        # ensure_ascii=False preserves Turkish and special characters

    print(f"✅ JSON exported: {output_file}")


# ═══════════════════════════════════════════════════════
# HEALTH CHECK
# ═══════════════════════════════════════════════════════

def health_check(db_name):
    """
    Checks database health.
    Verifies connection, lists tables, and counts patients.
    """
    results = {}

    # Test database connection
    try:
        with sqlite3.connect(db_name) as conn:
            conn.execute("SELECT 1")    # Simplest possible query
        results["connection"] = "✅ OK"
    except Exception as e:
        results["connection"] = f"❌ FAIL: {e}"

    with sqlite3.connect(db_name) as conn:
        # List all tables
        tables = conn.execute("""
            SELECT name FROM sqlite_master WHERE type='table'
        """).fetchall()
        results["tables"] = [t[0] for t in tables]  # Extract table name from each tuple

        # Count total patients
        results["patient_count"] = conn.execute(
            "SELECT COUNT(*) FROM patients"
        ).fetchone()[0]                 # fetchone() returns (3,), [0] gets 3

    results["checked_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    return results


# ═══════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════

def main():
    DB = "healthtrack.db"               # Database filename constant

    print("=" * 50)
    print("🏥 HealthTrack Mini Project")
    print("=" * 50)

    # Step 1: Initialize database
    setup_database(DB)

    # Step 2: Create patient objects
    patients = [
        Patient("Alice Kaya",   35, "P001", 70,  165),
        Patient("Bob Demir",    28, "P002", 95,  175),
        Patient("Carol Yıldız", 52, "P003", 45,  160),
    ]

    # Add medical records and medications
    patients[0].add_record("Annual checkup — normal")
    patients[0].add_record("Blood pressure: 120/80")
    patients[0].add_medication("Vitamin D")

    patients[1].add_record("Obesity consultation")
    patients[1].add_medication("Metformin")

    patients[2].add_record("Osteoporosis screening")
    patients[2].add_medication("Calcium")

    # Step 3: Save to database
    print("\n📥 Saving patients:")
    for p in patients:                  # Iterates through each Patient object
        save_patient(DB, p)

    # Step 4: List all patients
    print("\n📋 All Patients:")
    for row in get_all_patients(DB):
        print(f"  {row[1]:15} Age:{row[2]:4} Blood:{row[5]}")

    # Step 5: High risk patients
    print("\n🔴 High Risk Patients:")
    high_risk = get_high_risk(DB)
    if high_risk:                       # True if list is not empty
        for row in high_risk:
            print(f"  {row[0]:15} BMI: {row[2]}")
    else:
        print("  No high risk patients")

    # Step 6: Age range filter
    print("\n🔍 Patients aged 30-50:")
    for row in get_patients_by_age(DB, 30, 50):
        print(f"  {row[1]:15} Age: {row[2]}")

    # Step 7: Statistics
    print("\n📊 Statistics:")
    stats, bmi_groups, patient_records = get_statistics(DB)

    print(f"  Total patients : {stats['total']}")
    print(f"  Age range      : {stats['min_age']} - {stats['max_age']}")
    print(f"  Average age    : {stats['avg_age']}")

    print("\n  BMI Groups:")
    for category, count in bmi_groups:
        print(f"    {category:12} → {count} patients")

    print("\n  Record Counts:")
    for name, count in patient_records:
        print(f"    {name:15} → {count} records")

    # Step 8: Load a specific patient
    print("\n👤 Loading Alice:")
    alice = load_patient(DB, "P001")
    if alice:
        print(f"  {alice}")             # Calls Patient.__str__
        print(f"  Records: {len(alice)}")   # Calls Patient.__len__
        print(f"  Has records: {bool(alice)}")  # Calls Patient.__bool__

    # Step 9: Export to JSON
    print("\n💾 Exporting to JSON:")
    export_to_json(DB, "healthtrack_export.json")

    # Step 10: Health check
    print("\n🔧 Database Health Check:")
    results = health_check(DB)
    for key, value in results.items():
        print(f"  {key:20} → {value}")

    print("\n" + "=" * 50)
    print("✅ Mini Project Complete!")
    print("=" * 50)


if __name__ == "__main__":  # Only runs when executed directly, not when imported
    main()