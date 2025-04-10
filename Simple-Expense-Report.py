import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv
import re

# ---------------- DATABASE SETUP ----------------
def init_db():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            category TEXT,
            amount REAL,
            description TEXT
        )
    ''')
    conn.commit()
    return conn

# ---------------- VALIDATION ----------------
def validate_input(date, amount):
    date_pattern = r"^\d{4}-\d{2}-\d{2}$"
    amount_pattern = r"^\d+(\.\d{1,2})?$"
    if not re.match(date_pattern, date):
        messagebox.showerror("Invalid Input", "Date must be in YYYY-MM-DD format.")
        return False
    if not re.match(amount_pattern, amount):
        messagebox.showerror("Invalid Input", "Amount must be a valid number.")
        return False
    return True

# ---------------- CRUD FUNCTIONS ----------------
def add_expense(conn, date, category, amount, description, tree, entries):
    if not all([date, category, amount, description]):
        messagebox.showwarning("Input Required", "All fields are required.")
        return
    if validate_input(date, amount):
        cursor = conn.cursor()
        cursor.execute("INSERT INTO expenses (date, category, amount, description) VALUES (?, ?, ?, ?)",
                       (date, category, float(amount), description))
        conn.commit()
        messagebox.showinfo("Success", "Expense added!")
        for entry in entries:
            entry.delete(0, tk.END)
        refresh_expenses(conn, tree)

def delete_expense(conn, tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("No Selection", "Select an entry to delete.")
        return
    item = tree.item(selected[0])
    expense_id = item['values'][0]
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    messagebox.showinfo("Deleted", "Expense deleted.")
    refresh_expenses(conn, tree)

def export_expenses(conn):
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
    if file_path:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM expenses")
        rows = cursor.fetchall()
        with open(file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Date", "Category", "Amount", "Description"])
            writer.writerows(rows)
        messagebox.showinfo("Exported", "Expenses exported successfully!")

def refresh_expenses(conn, tree):
    for row in tree.get_children():
        tree.delete(row)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses ORDER BY date DESC")
    for row in cursor.fetchall():
        tree.insert('', 'end', values=row)

# ---------------- GUI ----------------
def build_ui():
    conn = init_db()
    root = tk.Tk()
    root.title("💸 Modern Expense Tracker")
    root.geometry("850x600")
    root.configure(bg="#f5f7fa")

    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"), background="#f0f0f0")
    style.configure("Treeview", font=("Segoe UI", 10), rowheight=28)
    style.map("Treeview", background=[('selected', '#cce5ff')])
    style.configure("TLabel", font=("Segoe UI", 10))
    style.configure("TEntry", font=("Segoe UI", 10))
    style.configure("TButton", font=("Segoe UI", 10), padding=6)

    # ---------- INPUT SECTION ----------
    input_frame = ttk.LabelFrame(root, text="Add New Expense", padding=20)
    input_frame.pack(padx=20, pady=10, fill="x")

    labels = ["Date (YYYY-MM-DD):", "Category:", "Amount:", "Description:"]
    entries = []

    for i, label_text in enumerate(labels):
        ttk.Label(input_frame, text=label_text).grid(row=i, column=0, sticky="e", padx=10, pady=8)
        entry = ttk.Entry(input_frame, width=40)
        entry.grid(row=i, column=1, pady=8, sticky="w")
        entries.append(entry)

    button_frame = ttk.Frame(input_frame)
    button_frame.grid(row=4, column=0, columnspan=2, pady=10)

    ttk.Button(button_frame, text="➕ Add Expense", width=18,
               command=lambda: add_expense(conn, entries[0].get(), entries[1].get(),
                                           entries[2].get(), entries[3].get(), tree, entries)).grid(row=0, column=0, padx=8)

    ttk.Button(button_frame, text="📤 Export to CSV", width=18,
               command=lambda: export_expenses(conn)).grid(row=0, column=1, padx=8)

    # ---------- LIST SECTION ----------
    list_frame = ttk.LabelFrame(root, text="All Expenses", padding=20)
    list_frame.pack(padx=20, pady=10, fill="both", expand=True)

    columns = ("ID", "Date", "Category", "Amount", "Description")
    tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", stretch=True)

    tree.pack(fill="both", expand=True)

    ttk.Button(root, text="🗑️ Delete Selected", width=20,
               command=lambda: delete_expense(conn, tree)).pack(pady=10)

    refresh_expenses(conn, tree)

    root.mainloop()

# 🔥 Launch the app
build_ui()
