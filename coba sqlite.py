import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

DB_NAME = 'scool.db'

def run_query(sql, params=()):
    conn = sqlite3.connect (DB_NAME)
    try:
        with conn:
            return conn.execute(sql, params).fetchall()
    finally:
        conn.close()

def init_db():
    run_query('''CREATE TABLE IF NOT EXISTS student (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,age INTEGER,major TEXT)''')

def add_student(name, age, major):
    run_query('''INSERT INTO student (name, age, major) VALUES (?, ?, ?)''', 
              (name, age, major))

def get_students():
    return run_query('SELECT id, name, age, major FROM student ORDER BY name')

def update_student (sid, name, age, major):
    run_query('''UPDATE student SET name = ?, age = ?, major = ? WHERE id = ?''', 
              (name, age, major, sid))  

def delete_student(sid):
    run_query('DELETE FROM student WHERE id = ?', (sid,))

init_db()
root = tk.Tk()
root.title("Student Manager")

entries = {}
for i, field in enumerate(['Name', 'Age', 'Major']):
    tk.Label(root, text=field).grid(row=i, column=0)
    entries[field] = tk.Entry(root, width=30)
    entries[field].grid(row=i, column=1, pady=4)

cols = ('id', 'name', 'age', 'major')
tree = ttk.Treeview(root, columns=cols, 
                    show='headings')
for c in cols:
    tree.heading(c, text=c.title())
tree.grid_removegrid(row=4, column=0, columnspan=2)

def read_from():
    name = entries['Name'].get().strip()
    age = entries['Age'].get().strip()
    major = entries['Major'].get().strip()
    if not name or not age:
        messagebox.showwarning("Missing data", "Name and Age are needed.")
        return None
    if not age.isdigit():
        messagebox.showwarning("Invalid age", "Age must be a number.")
        return None
    return name, int(age), major

def on_add():
    data = read_from()
    if data:
        add_student(*data)
        clear_form()
        refresh()

#Load database rows into the table
def refresh():
    tree.delete(*tree.get_children())
    for row in get_students():
        tree.insert('', tk.END, values=row)

#Reset the form
def clear_form():
    global selected_id
    selected_id = None
    for e in entries.values():
        e.delete(0, tk.END)

btns = tk.Frame(root)
btns.grid(row=3, column=0, columnspan=2, pady=4)
for text, cmd in [('Add', on_add), ('Update', on_update), 
                  ('Delete', on_delete), ('Clear', clear_form)]:
    tk.Button(btns, text=text, width=8, command=cmd).pack(side='LEFT', padx=4)
refresh(); root.mainloop()

#click a row to load it

def on_select(event):
    global selected_id
    sel = tree.selection()
    if not sel:
        return
    sid, name, age, major = \
        tree.item(sel[0], 'values')
    clear_form()
    selected_id = int(sid)
    entries['Name'].insert(0, name)
    entries['Age'].insert(0, age)
    entries['Major'].insert(0, major)

tree.bind('<<TreeviewSelect>>', on_select)

#act on the selected id
def on_update():
    if selected_id is None:
        messagebox.showinfo("Update",
             "Select a student first.")
        return
    data = read_from()
    if data:
        update_student(selected_id, *data)
        clear_form(); refresh()

def on_delete():
    ... # same check, then
    if messagebox.askyesno("Confirm", 
            "Delete this student?"):
        delete_student(selected_id)
        clear_form(); refresh()