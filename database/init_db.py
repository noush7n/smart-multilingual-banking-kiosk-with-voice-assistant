"""Create and fill the database:  python database/init_db.py
WARNING: running this deletes all existing data and starts fresh."""
import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from werkzeug.security import generate_password_hash

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "kiosk.db"
SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"

# (account_number, holder_name, account_type, pin, monthly_salary_paise, random_seed)
ACCOUNTS = [
    ("301245670011", "Ananya Sharma", "Savings", "1234", 5500000, 1),
    ("301245670022", "Rajesh Verma", "Savings", "4321", 4200000, 2),
    ("301245670033", "Meera Iyer", "Current", "2580", 7800000, 3),
]

# People who "write" cheques (used to check a cheque is genuine)
ISSUERS = [
    ("501100200301", "Sunrise Traders"),
    ("501100200302", "Kavita Joshi"),
    ("501100200303", "Metro Electricals"),
    ("501100200304", "Arjun Nair"),
]

# (channel, description, (min_paise, max_paise))
DEBITS = [
    ("UPI", "UPI payment - Grocery Mart", (30000, 250000)),
    ("UPI", "UPI payment - Fuel Station", (100000, 300000)),
    ("ATM", "ATM cash withdrawal", (200000, 1000000)),
    ("BILL", "Electricity bill payment", (80000, 350000)),
    ("BILL", "Mobile recharge", (24900, 99900)),
    ("POS", "Card payment - City Mall", (150000, 600000)),
    ("NEFT", "Rent transfer", (800000, 1200000)),
]
CREDITS = [
    ("UPI", "UPI received from friend", (50000, 300000)),
    ("INTEREST", "Interest credit", (10000, 60000)),
    ("NEFT", "Refund received", (20000, 150000)),
]

OPENING_BALANCE = 2500000  # Rs 25,000.00 in paise


def build_events(rng, salary, now):
    events = []
    for days_ago in (85, 55, 25):
        events.append((now - timedelta(days=days_ago), "CREDIT", "SALARY", "Salary credit", salary))
    for _ in range(14):
        when = now - timedelta(days=rng.randint(1, 80), hours=rng.randint(0, 10))
        if rng.random() < 0.8:
            kind = "DEBIT"
            channel, desc, (low, high) = rng.choice(DEBITS)
        else:
            kind = "CREDIT"
            channel, desc, (low, high) = rng.choice(CREDITS)
        amount = rng.randint(low // 100, high // 100) * 100  # whole rupees
        events.append((when, kind, channel, desc, amount))
    events.sort(key=lambda e: e[0])
    return events


def main():
    db = sqlite3.connect(DB_PATH)
    db.execute("PRAGMA foreign_keys = ON")
    db.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))

    now = datetime.now()
    counter = 0

    for number, name, acc_type, pin, salary, seed in ACCOUNTS:
        cur = db.execute(
            "INSERT INTO accounts (account_number, holder_name, account_type, pin_hash) "
            "VALUES (?, ?, ?, ?)",
            (number, name, acc_type, generate_password_hash(pin)),
        )
        account_id = cur.lastrowid
        balance = OPENING_BALANCE
        txn_ids = []

        for when, kind, channel, desc, amount in build_events(random.Random(seed), salary, now):
            if kind == "DEBIT" and amount > balance:
                continue  # never let the balance go negative
            balance += amount if kind == "CREDIT" else -amount
            counter += 1
            reference = f"TXN-{when:%Y%m%d}-{counter:06d}"
            cur = db.execute(
                "INSERT INTO transactions (reference_no, account_id, txn_date, txn_type, "
                "channel, description, amount_paise, balance_after_paise) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (reference, account_id, when.strftime("%Y-%m-%d %H:%M:%S"),
                 kind, channel, desc, amount, balance),
            )
            txn_ids.append(cur.lastrowid)

        # Leave the last 5 transactions "not yet printed" in the passbook
        last_printed = txn_ids[-6] if len(txn_ids) > 6 else 0
        db.execute(
            "UPDATE accounts SET balance_paise = ?, passbook_last_txn_id = ? WHERE id = ?",
            (balance, last_printed, account_id),
        )

    db.executemany("INSERT INTO demo_issuers (issuer_account_no, issuer_name) VALUES (?, ?)", ISSUERS)
    db.execute(
        "INSERT INTO admin (username, password_hash) VALUES (?, ?)",
        ("admin", generate_password_hash("admin123")),
    )
    db.commit()
    db.close()

    print("Database created:", DB_PATH)
    print("Accounts: 3  | Account PINs: 1234, 4321, 2580  | Admin login: admin / admin123")


if __name__ == "__main__":
    main()