# Enhanced Task Manager 🗂️

A command-line application to manage employees, tasks, and tags — built with Python and SQLite as part of the SQL & Database I course at Al-Hussein Technical University (HTU).

> Grade: 10/10 ✅

---

## What it does

A company manager can use this app to:
- Add and manage **employees** (users)
- Assign and track **tasks** per employee
- Organise tasks using **tags** (categories)
- View detailed reports directly in the terminal

All data is stored in a local SQLite database with full **foreign-key enforcement**.

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3 | Core language |
| SQLite3 | Local relational database (built-in) |
| inquirer | Arrow-key menus in the terminal |
| PrettyTable | Clean table output |
| art + termcolor | Banners and coloured text |

---

## Database Schema

Five tables with proper relationships:

| Table | Description |
|-------|-------------|
| `Users` | Name and email |
| `UserDetails` | Phone, preferences, address |
| `Tasks` | Description, due date, status |
| `Tags` | Category labels |
| `tasks_tags` | Links tasks to tags (many-to-many) |

---

## Getting Started

```bash
git clone https://github.com/Mahmoud-Qwaider/enhanced-task-manager.git
cd enhanced-task-manager
pip install -r requirements.txt
python main.py
```

The database (`todo_list.db`) is created automatically on first run.

---

## Project Structure

---

## How I Built This

1. Designed the database schema (5 tables with FK relationships)
2. Wrote pseudocode for each CRUD operation
3. Implemented the database layer in `sql.py`
4. Built the CLI interface in `main.py`
5. Fixed foreign-key enforcement bug in `get_connection()`
6. Added error handling and input validation
7. Tested all 21 menu options manually

---

## About

Built by **Mahmoud Quaider** — AI student at Al-Zaytoonah University of Jordan  
Course: SQL & Database I — HTU, 2026
