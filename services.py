import csv
from datetime import datetime
from pathlib import Path

# ---------------- Paths ----------------
DATA_PATH = Path(__file__).parent / "data"
CUSTOMERS_CSV = DATA_PATH / "customers.csv"
ADDED_CSV = DATA_PATH / "added_customers.csv"
DELETED_CSV = DATA_PATH / "deleted_customers.csv"
DUES_CSV = DATA_PATH / "dues.csv"
LOGS_CSV = DATA_PATH / "logs.csv"

# ---------------- Helper Functions ----------------
def _read_csv(file, fieldnames=None):
    if not file.exists():
        return []
    with open(file, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

def _write_csv(file, rows, fieldnames):
    file.parent.mkdir(parents=True, exist_ok=True)
    with open(file, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def _append_csv(file, row, fieldnames):
    rows = _read_csv(file, fieldnames)
    rows.append(row)
    _write_csv(file, rows, fieldnames)

def _log_action(action, details=""):
    LOGS_CSV.parent.mkdir(parents=True, exist_ok=True)
    entry = [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), action, details]
    with open(LOGS_CSV, "a", newline='', encoding="utf-8") as f:
        csv.writer(f).writerow(entry)

def _next_id():
    customers = _read_csv(CUSTOMERS_CSV)
    return max((int(c["id"]) for c in customers), default=0) + 1

def _save_due(customer):
    _append_csv(
        DUES_CSV,
        {
            "id": customer["id"],
            "name": customer["name"],
            "due": customer["due"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        ["id", "name", "due", "timestamp"]
    )

# ---------------- Core Services ----------------
def add_customer(name, phone, email, address, due):
    customers = _read_csv(CUSTOMERS_CSV)
    new_customer = {
        "id": str(_next_id()),
        "name": name.strip(),
        "phone": phone.strip(),
        "email": email.strip(),
        "address": address.strip(),
        "due": str(float(due)),
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "active"
    }
    customers.append(new_customer)
    _write_csv(CUSTOMERS_CSV, customers, new_customer.keys())

    _append_csv(ADDED_CSV, new_customer, new_customer.keys())
    _save_due(new_customer)
    _log_action("Add Customer", f"Added {name}, ID={new_customer['id']}, Due={due}")
    return new_customer

def delete_customer(customer_id):
    customers = _read_csv(CUSTOMERS_CSV)
    filtered = [c for c in customers if int(c["id"]) != customer_id]
    if len(filtered) == len(customers):
        return False

    deleted_cust = next(c for c in customers if int(c["id"]) == customer_id)
    _write_csv(CUSTOMERS_CSV, filtered, customers[0].keys())

    _append_csv(DELETED_CSV, deleted_cust, deleted_cust.keys())
    _save_due(deleted_cust)
    _log_action("Delete Customer", f"Deleted {deleted_cust['name']}, ID={customer_id}, Due={deleted_cust['due']}")
    return True

def delete_all_customers():
    customers = _read_csv(CUSTOMERS_CSV)
    if not customers:
        return False

    _write_csv(CUSTOMERS_CSV, [], customers[0].keys())
    for cust in customers:
        _append_csv(DELETED_CSV, cust, cust.keys())
        _save_due(cust)
    _log_action("Delete All Customers", f"Deleted all {len(customers)} customers")
    return True

def get_all_customers():
    return _read_csv(CUSTOMERS_CSV)
