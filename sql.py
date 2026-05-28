# PSEUDOCODE - sql.py (Database Layer).py
# ============================================================================
# Database layer for the Enhanced Task Manager.
# Contains the connection helper, schema creation, and all CRUD functions
# for Users, UserDetails, Tags, Tasks, and the tasks_tags junction table.
# All queries use ? placeholders to prevent SQL injection.
# ============================================================================

import sqlite3


def get_connection():
    # Opens a connection to the database. We turn foreign-key enforcement ON
    # for EVERY connection because SQLite disables it by default on each new
    # connection — this makes FK constraints actually work for all operations.
    conn = sqlite3.connect('todo_list.db')
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def create_db():
    # Creates all tables if they don't exist yet. Unchanged from the original
    # schema so existing databases keep working.
    conn = get_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS Users(
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT
        );
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS UserDetails(
            user_details_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            phone_number TEXT,
            preferences TEXT,
            address TEXT,
            FOREIGN KEY(user_id) REFERENCES Users(user_id)
        );
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS Tags(
            tag_id INTEGER PRIMARY KEY,
            name TEXT
        );
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS Tasks(
            task_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            description TEXT,
            due_date DATE,
            status TEXT,
            FOREIGN KEY (user_id) REFERENCES Users(user_id)
        );
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tasks_tags(
            task_id INTEGER,
            tag_id INTEGER,
            PRIMARY KEY(task_id, tag_id),
            FOREIGN KEY (task_id) REFERENCES Tasks(task_id),
            FOREIGN KEY (tag_id) REFERENCES Tags(tag_id)
        );
    ''')
    conn.commit()
    conn.close()


# =============== Users ===============

def read_users():
    # Returns all users as a list of (user_id, name, email) tuples.
    conn = get_connection()
    cursor = conn.execute('SELECT * FROM Users')
    users = cursor.fetchall()
    conn.close()
    return users


def create_user(name, email):
    # Inserts a new user record.
    conn = get_connection()
    conn.execute('INSERT INTO Users (name, email) VALUES (?, ?)', (name, email))
    conn.commit()
    conn.close()


def read_user(user_id):
    # Returns a single user tuple, or None if the ID doesn't exist.
    conn = get_connection()
    cursor = conn.execute('SELECT * FROM Users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user


def update_user_info(user_id, name, email):
    # RENAMED from update_user(). Updates a user's name and email.
    # Returns the number of affected rows so the UI can tell if the ID existed.
    conn = get_connection()
    cursor = conn.execute(
        'UPDATE Users SET name = ?, email = ? WHERE user_id = ?',
        (name, email, user_id)
    )
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected


def delete_user(user_id):
    # Removes a user. Because FK enforcement is ON, deleting a user that still
    # has UserDetails or Tasks would fail. So we first remove the dependent
    # records (and their tag links), then delete the user — no orphan rows left.
    conn = get_connection()
    try:
        conn.execute('DELETE FROM tasks_tags WHERE task_id IN (SELECT task_id FROM Tasks WHERE user_id = ?)', (user_id,))
        conn.execute('DELETE FROM Tasks WHERE user_id = ?', (user_id,))
        conn.execute('DELETE FROM UserDetails WHERE user_id = ?', (user_id,))
        cursor = conn.execute('DELETE FROM Users WHERE user_id = ?', (user_id,))
        conn.commit()
        return cursor.rowcount
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Database error: {e}")
        return 0
    finally:
        conn.close()


# =============== UserDetails ===============

def create_user_details(user_id, phone, preferences, address):
    # Inserts extended info for a user. Validates that the user exists first
    # so we don't create details pointing to a non-existent user.
    conn = get_connection()
    try:
        conn.execute(
            'INSERT INTO UserDetails (user_id, phone_number, preferences, address)'
            ' VALUES (?, ?, ?, ?)',
            (user_id, phone, preferences, address)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        conn.rollback()
        print(f"Cannot create details (invalid user_id?): {e}")
        return False
    finally:
        conn.close()


def read_user_details(user_details_id):
    # Returns a single UserDetails row by its primary key, or None.
    conn = get_connection()
    cursor = conn.execute(
        'SELECT * FROM UserDetails WHERE user_details_id = ?',
        (user_details_id,)
    )
    details = cursor.fetchone()
    conn.close()
    return details


def view_user_details(user_id):
    # NEW. Returns a combined view of a user plus their extended details by
    # joining Users and UserDetails on user_id. We use a LEFT JOIN so a user
    # with no details row still shows up (with NULLs in the detail columns).
    # Returns a tuple, or None if the user doesn't exist at all.
    conn = get_connection()
    cursor = conn.execute('''
        SELECT u.user_id, u.name, u.email,
               d.phone_number, d.preferences, d.address
        FROM Users u
        LEFT JOIN UserDetails d ON u.user_id = d.user_id
        WHERE u.user_id = ?
    ''', (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row


def update_user_details(user_details_id, phone, preferences, address):
    # Updates an existing UserDetails row. Returns affected row count.
    conn = get_connection()
    cursor = conn.execute(
        'UPDATE UserDetails SET phone_number = ?, preferences = ?, address = ?'
        ' WHERE user_details_id = ?',
        (phone, preferences, address, user_details_id)
    )
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected


def delete_user_details(user_details_id):
    # Removes a single extended-info row by its primary key.
    conn = get_connection()
    cursor = conn.execute(
        'DELETE FROM UserDetails WHERE user_details_id = ?',
        (user_details_id,)
    )
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected


# =============== Tags ===============

def read_tags():
    # Helper: returns all tags. Useful for the UI to list available tags.
    conn = get_connection()
    cursor = conn.execute('SELECT * FROM Tags')
    tags = cursor.fetchall()
    conn.close()
    return tags


def create_tag(name):
    # Inserts a new tag.
    conn = get_connection()
    conn.execute('INSERT INTO Tags (name) VALUES (?)', (name,))
    conn.commit()
    conn.close()


def update_tag_name(tag_id, new_name):
    # NEW. Renames an existing tag. Returns affected row count so the UI can
    # report whether the tag_id was valid.
    conn = get_connection()
    cursor = conn.execute(
        'UPDATE Tags SET name = ? WHERE tag_id = ?',
        (new_name, tag_id)
    )
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected


def delete_tag(tag_id):
    # NEW. Deletes a tag. Since the tag may still be linked to tasks via
    # tasks_tags (FK enforcement is ON), we first unlink it everywhere, then
    # delete the tag itself.
    conn = get_connection()
    try:
        conn.execute('DELETE FROM tasks_tags WHERE tag_id = ?', (tag_id,))
        cursor = conn.execute('DELETE FROM Tags WHERE tag_id = ?', (tag_id,))
        conn.commit()
        affected = cursor.rowcount
        return affected
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Database error while deleting tag: {e}")
        return 0
    finally:
        conn.close()


# =============== Tasks ===============

def read_tasks():
    # Returns all tasks.
    conn = get_connection()
    cursor = conn.execute('SELECT * FROM Tasks')
    tasks = cursor.fetchall()
    conn.close()
    return tasks


def create_task(user_id, description, due_date, status):
    # Inserts a new task. Validates the user exists (FK) to avoid orphan tasks.
    conn = get_connection()
    try:
        conn.execute(
            'INSERT INTO Tasks (user_id, description, due_date, status)'
            ' VALUES (?, ?, ?, ?)',
            (user_id, description, due_date, status)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        conn.rollback()
        print(f"Cannot create task (invalid user_id?): {e}")
        return False
    finally:
        conn.close()


def read_task(task_id):
    # Returns a single task tuple, or None.
    conn = get_connection()
    cursor = conn.execute('SELECT * FROM Tasks WHERE task_id = ?', (task_id,))
    task = cursor.fetchone()
    conn.close()
    return task


def update_task_details(task_id, description, due_date, status):
    # RENAMED from update_task(). Updates a task's description, due date,
    # and status. Returns affected row count.
    conn = get_connection()
    cursor = conn.execute(
        'UPDATE Tasks SET description = ?, due_date = ?, status = ? WHERE task_id = ?',
        (description, due_date, status, task_id)
    )
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected


def mark_task_complete(task_id):
    # NEW. Dedicated completion feature: sets a task's status to 'Completed'
    # without touching its description or due date. Returns affected row count.
    conn = get_connection()
    cursor = conn.execute(
        "UPDATE Tasks SET status = 'Completed' WHERE task_id = ?",
        (task_id,)
    )
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected


def delete_task(task_id):
    # Removes a task. First unlinks any tags attached to it (FK enforcement),
    # then deletes the task itself so we leave no orphan rows in tasks_tags.
    conn = get_connection()
    try:
        conn.execute('DELETE FROM tasks_tags WHERE task_id = ?', (task_id,))
        cursor = conn.execute('DELETE FROM Tasks WHERE task_id = ?', (task_id,))
        conn.commit()
        return cursor.rowcount
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Database error: {e}")
        return 0
    finally:
        conn.close()


# =============== TaskTag (junction) ===============

def create_task_tag_relation(task_id, tag_id):
    # Links a tag to a task. Guards against invalid IDs and duplicate links.
    conn = get_connection()
    try:
        conn.execute(
            'INSERT INTO tasks_tags (task_id, tag_id) VALUES (?, ?)',
            (task_id, tag_id)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        conn.rollback()
        print(f"Cannot assign tag (invalid IDs or already linked?): {e}")
        return False
    finally:
        conn.close()


def list_tags_for_task(task_id):
    # RENAMED from read_tags_for_task(). Returns full tag rows (id, name)
    # for every tag linked to the given task by joining tasks_tags with Tags.
    # (The original only returned tag_ids; joining lets the UI show names too.)
    conn = get_connection()
    cursor = conn.execute('''
        SELECT t.tag_id, t.name
        FROM tasks_tags tt
        JOIN Tags t ON tt.tag_id = t.tag_id
        WHERE tt.task_id = ?
    ''', (task_id,))
    tags = cursor.fetchall()
    conn.close()
    return tags


def list_tasks_for_tag(tag_id):
    # RENAMED from read_tasks_for_tag(). Returns full task rows for every task
    # linked to the given tag by joining tasks_tags with Tasks.
    conn = get_connection()
    cursor = conn.execute('''
        SELECT t.task_id, t.user_id, t.description, t.due_date, t.status
        FROM tasks_tags tt
        JOIN Tasks t ON tt.task_id = t.task_id
        WHERE tt.tag_id = ?
    ''', (tag_id,))
    tasks = cursor.fetchall()
    conn.close()
    return tasks


def remove_tag_from_task(task_id, tag_id):
    # RENAMED from delete_task_tag_relation(). Unlinks a tag from a task
    # without deleting either the tag or the task. Returns affected row count.
    conn = get_connection()
    cursor = conn.execute(
        'DELETE FROM tasks_tags WHERE task_id = ? AND tag_id = ?',
        (task_id, tag_id)
    )
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected


if __name__ == '__main__':
    create_db()