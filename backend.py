import snowflake.connector
from config import SNOWFLAKE_USER, SNOWFLAKE_PASSWORD, SNOWFLAKE_ACCOUNT, SNOWFLAKE_DATABASE, SNOWFLAKE_SCHEMA, SNOWFLAKE_WAREHOUSE




# Connect to Snowflake
import streamlit as st
import snowflake.connector

def get_connection():
    return snowflake.connector.connect(
        user=st.secrets["SNOWFLAKE_USER"],
        password=st.secrets["SNOWFLAKE_PASSWORD"],
        account=st.secrets["SNOWFLAKE_ACCOUNT"],
        warehouse=st.secrets["SNOWFLAKE_WAREHOUSE"],
        database=st.secrets["SNOWFLAKE_DATABASE"],
        schema=st.secrets["SNOWFLAKE_SCHEMA"],
    )


def login_admin(email, password):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT admin_id FROM admins WHERE email = %s AND password = %s;", (email, password))
        admin = cur.fetchone()
        
        if admin:
            return {"admin_id": admin[0]}  # Successful login

        return None  # Invalid login

    except Exception as e:
        print(f"Error: {e}")
        return None

    finally:
        cur.close()
        conn.close()



def get_project_tasks():
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT client_name, task_name, description,priority,assigned_status, due_date, task_id FROM project_task_table")
        tasks = cur.fetchall()
        return tasks  # Returns a list of tuples
    
    except Exception as e:
        print(f"Error fetching tasks: {e}")
        return []
    
    finally:
        cur.close()
        conn.close()



def get_all_employees():
    conn = get_connection()
    cur = conn.cursor()

    try:
        # Fetch employee details (excluding passwords for security)
        cur.execute("SELECT employee_id, employee_name, email FROM employee_logins")
        employees = cur.fetchall()
        return employees  # Returns a list of tuples (employee_id, employee_name, email, created_at)

    except Exception as e:
        print(f"Error fetching employees: {e}")
        return []

    finally:
        cur.close()
        conn.close()


def update_task(task_id, new_description, new_due_date):
    conn = get_connection()
    cur = conn.cursor()

    try:
        # Update task details in the database
        query = "UPDATE project_task_table SET description = %s, due_date = %s WHERE task_id = %s"
        cur.execute(query, (new_description, new_due_date, task_id))

        conn.commit()  # Explicitly commit changes
        return True  # Indicate success
    
    except Exception as e:
        print(f"Error updating task: {e}")
        return False  # Indicate failure

    finally:
        cur.close()
        conn.close()

def assign_task_to_employee(task_id, assigned_by, employee_id):
    conn = get_connection()
    cur = conn.cursor()

    try:
        query = """
        INSERT INTO Pending_task_table (task_id, assigned_by, employee_id)
        VALUES (%s, %s, %s)
        """
        cur.execute(query, (task_id, assigned_by, employee_id))

        cur.execute("""
            UPDATE Project_task_table
            SET assigned_status = 'Assigned'
            WHERE task_id = %s
        """, (task_id,))



        conn.commit()  # Save changes
        return True  # Success

    except Exception as e:
        print(f"Error assigning task: {e}")
        return False  # Failure

    finally:
        cur.close()
        conn.close()

def add_client(client_name, email, phone):
    conn = get_connection()
    cur = conn.cursor()

    try:
        query = "INSERT INTO clients (client_id, client_name, email, phone) VALUES (DEFAULT, %s, %s, %s)"
        cur.execute(query, (client_name, email, phone))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding client: {e}")
        return False
    finally:
        cur.close()
        conn.close()


def add_employee(employee_name, email, password):
    conn = get_connection()
    cur = conn.cursor()

    try:
        query = "INSERT INTO employee_logins (employee_id, employee_name, email, password) VALUES (DEFAULT, %s, %s, %s)"
        cur.execute(query, (employee_name, email, password))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding employee: {e}")
        return False
    finally:
        cur.close()
        conn.close()

def get_all_clients():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT client_id, client_name, email, phone, created_at FROM clients")
    clients = cursor.fetchall()
    conn.close()
    return clients


print("Backend has started ")



def get_total_clients():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM clients")
    total = cursor.fetchone()[0]
    conn.close()
    return total

def get_total_employees():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM employee_logins")
    total = cursor.fetchone()[0]
    conn.close()
    return total

def get_total_tasks():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Project_task_table")
    total = cursor.fetchone()[0]
    conn.close()
    return total

def get_pending_tasks():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM pending_task_table")
    total = cursor.fetchone()[0]
    conn.close()
    return total

def get_completed_tasks():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM employee_task_table WHERE status = 'Completed'")
    total = cursor.fetchone()[0]
    conn.close()
    return total

def get_in_progress_tasks():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM employee_task_table ")
    total = cursor.fetchone()[0]
    conn.close()
    return total

def submit_idea(name, idea_text):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Idea (Idea, Name)
        VALUES (%s, %s)
    """, (idea_text, name))
    conn.commit()
    conn.close()
    return True

def get_all_ideas():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Name, Idea FROM Idea ")
    ideas = cursor.fetchall()
    conn.close()
    return ideas



def login_employee(email, password):
    # Query your employee table to validate credentials
    # Example using Snowflake:
    cursor = get_connection().cursor()
    query = """
        SELECT employee_id FROM employee_logins
        WHERE email = %s AND password = %s
    """
    cursor.execute(query, (email, password))
    result = cursor.fetchone()
    return {"employee_id": result[0]} if result else None


def get_pending_tasks_for_assignment():
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT pt.pending_task_id, pt.task_id, pj.task_name, pj.description, pt.created_at
        FROM Pending_task_table pt
        JOIN Project_task_table pj ON pt.task_id = pj.task_id
        ORDER BY pt.created_at ASC
    """
    cursor.execute(query)
    return cursor.fetchall()

def assign_task_from_pending(pending_task_id, employee_id):
    conn = get_connection()
    cursor = conn.cursor()

    # Step 1: Get task_id from Pending_task_table
    cursor.execute("SELECT task_id FROM Pending_task_table WHERE pending_task_id = %s", (pending_task_id,))
    result = cursor.fetchone()
    if not result:
        return False

    task_id = result[0]

    try:
        # Step 2: Insert into Employee_task_table
        cursor.execute("""
            INSERT INTO Employee_task_table (employee_id, task_id, status)
            VALUES (%s, %s, 'To Do')
        """, (employee_id, task_id))

        # Step 3: Update Project_task_table assigned_status to 'Processing'
        cursor.execute("""
            UPDATE Project_task_table
            SET assigned_status = 'Processing'
            WHERE task_id = %s
        """, (task_id,))

        # Step 4: Delete from Pending_task_table
        cursor.execute("""
            DELETE FROM Pending_task_table
            WHERE pending_task_id = %s
        """, (pending_task_id,))

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("Error during assignment:", e)
        return False

def get_all_employee_tasks():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT employee_task_id, employee_id, task_id, assignment_date, completion_date, status,Task_Description,No_of_hours
        FROM Employee_task_table
        ORDER BY assignment_date DESC
    """)
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    conn.close()
    
    import pandas as pd
    return pd.DataFrame(rows, columns=columns)


def submit_help_request(name, help_text):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO Help (Name, Helps) VALUES (%s, %s)", (name, help_text))
        conn.commit()
        return True
    except Exception as e:
        print("Help submission error:", e)
        return False


def get_all_help_requests():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT Name, Helps FROM Help ORDER BY Name")
        return cur.fetchall()
    except Exception as e:
        print("Help fetch error:", e)
        return []


def update_employee_task(employee_task_id, completion_date, description, hours):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute( """
    UPDATE Employee_task_table
    SET completion_date = %s, Task_Description = %s, No_of_hours = %s
    WHERE task_id = %s
    """,
    (completion_date, description, hours, employee_task_id))
    conn.commit()
    conn.close()

