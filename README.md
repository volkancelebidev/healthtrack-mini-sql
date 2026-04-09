# HealthTrack Mini SQL

A lightweight clinic management system backed by SQLite, extending the 
original HealthTrack project with persistent database storage and 
structured querying.

Built to practice SQL integration with Python, covering CRUD operations,
JOIN queries, statistical reporting, and data export.

---

## Problem It Solves

The original HealthTrack stored data in JSON files — data was lost on 
restart and querying was limited. This version moves to a relational 
database, enabling persistent storage, complex filtering, and 
aggregated reporting.

---

## Features

- **Patient Management** — full CRUD with medical records and medication tracking
- **BMI Risk Assessment** — automatic High / Medium / Normal classification
- **Statistical Reporting** — aggregated health metrics via SQL GROUP BY
- **JSON Export** — structured data export with generation timestamp
- **Database Health Check** — record count summary across all tables

---

## Tech Stack

| Layer       | Technology                        |
|-------------|-----------------------------------|
| Language    | Python 3.12                       |
| Database    | SQLite (via built-in sqlite3)     |
| Paradigm    | OOP — Repository Pattern          |
| Export      | JSON                              |

---

## Project Structure
```
healthtrack-mini-sql/
├── models.py          # Patient domain model with BMI calculation
├── sql_mini_project.py # Database access and CRUD operations
└── utils.py           # Helper functions and data export
```
---

## How to Run

```bash
git clone https://github.com/volkancelebidev/healthtrack-mini-sql.git
cd healthtrack-mini-sql
python main.py
```

---

## What I Learned

This project was built to practice and consolidate:
- Connecting Python to SQLite using the sqlite3 module
- Designing relational schemas with PRIMARY KEY and FOREIGN KEY constraints
- Writing JOIN, GROUP BY, and aggregate SQL queries
- Implementing the Repository Pattern to separate data access from business logic
- Exporting structured data to JSON with proper encoding
