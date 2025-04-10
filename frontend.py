import streamlit as st
from datetime import datetime
import pandas as pd
from backend import (
    login_admin, get_project_tasks, get_all_employees,
    update_task, assign_task_to_employee, add_client, add_employee,
    get_all_clients, get_total_clients, get_total_employees, get_total_tasks,
    get_pending_tasks,submit_help_request,update_employee_task,get_all_employee_tasks,get_all_help_requests,get_pending_tasks_for_assignment,assign_task_from_pending, login_employee,get_completed_tasks, get_in_progress_tasks, submit_idea, get_all_ideas
)

# Page Configurations
st.set_page_config(
    page_title="Time Management System",
    page_icon="⏳",
    layout="wide"
)

# Custom Styling
st.markdown("""
    <style>
        .big-font { font-size: 30px !important; font-weight: bold; color: #4CAF50; }
        .subtext { font-size: 18px; color: #666; }
        .stButton>button { width: 100%; font-size: 16px; padding: 8px; }
        .sidebar-title { font-size: 22px; font-weight: bold; color: #2E86C1; }
        .center-text { text-align: center; }
        .box { 
            padding: 15px; 
            border: 2px solid #ddd; 
            border-radius: 10px; 
            background-color: #f9f9f9; 
            margin-bottom: 20px; 
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.user_id = None

# Sidebar Login
st.sidebar.markdown('<p class="sidebar-title">🔐 Login</p>', unsafe_allow_html=True)
login_option = st.sidebar.radio("Select Login Type:", ["Admin", "Employee"])

# Admin Login
if login_option == "Admin":
    email = st.sidebar.text_input("👤 Admin Username", "")
    password = st.sidebar.text_input("🔑 Admin Password", type="password")

    if st.sidebar.button("Login"):
        if not email.endswith("@bytepx.com"):
            st.sidebar.error("❌ You can't log in. Use a @bytepx.com email.")
        else:
            admin_info = login_admin(email, password)
            if admin_info:
                st.session_state.logged_in = True
                st.session_state.user_id = admin_info["admin_id"]
                st.session_state.user_role = "admin"
                st.sidebar.success(f"✅ Logged in as Admin ({email})")
                st.rerun()
            else:
                st.sidebar.error("❌ Invalid admin credentials!")

# Sidebar Idea Form
st.sidebar.markdown("## 💡 Share Your Idea")
with st.sidebar.form("idea_form"):
    idea_name = st.text_input("Your Name")
    idea_text = st.text_area("Your Idea")
    submitted = st.form_submit_button("Submit Idea")

    if submitted:
        if idea_name and idea_text:
            success = submit_idea(idea_name, idea_text)
            if success:
                st.sidebar.success("✅ Idea submitted successfully!")
        else:
            st.sidebar.error("❌ Please fill in both fields.")

# Public Ideas Display
st.markdown("### 💬 Community Ideas Board")
all_ideas = get_all_ideas()
if all_ideas:
    for name, idea in all_ideas:
        st.markdown(f"""
        <div style="border: 1px solid #ddd; padding: 10px; border-radius: 10px; margin-bottom: 10px; background-color: #f0f0f0;">
            <strong>🧠 {name} says:</strong> <br>
            {idea}
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("No ideas shared yet. Be the first!")

# Admin Panel
if st.session_state.logged_in and st.session_state.user_role == "admin":
    st.title("👑 Admin Panel")
    st.markdown("#### ⚙️ Manage employees, track productivity, and monitor performance.")

    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        st.metric(label="👥 Total Clients", value=get_total_clients())
    with kpi2:
        st.metric(label="🧑‍💼 Total Employees", value=get_total_employees())
    with kpi3:
        st.metric(label="🗂️ Total Tasks", value=get_total_tasks())

    kpi4, kpi5, kpi6 = st.columns(3)
    with kpi4:
        st.metric(label="⏳ Pending Tasks", value=get_pending_tasks())
    with kpi5:
        st.metric(label="🚧 In Progress", value=get_in_progress_tasks())
    with kpi6:
        st.metric(label="✅ Completed Tasks", value=get_completed_tasks())

    col1, col2 = st.columns(2)

    # Add New Client
    with col1:
        st.markdown('<div class="box">', unsafe_allow_html=True)
        st.markdown("### ➕ Add New Client")
        client_name = st.text_input("Client Name")
        client_email = st.text_input("Client Email")
        client_phone = st.text_input("Client Phone")
        if st.button("Add Client"):
            success = add_client(client_name, client_email, client_phone)
            if success:
                st.success(f"✅ Client {client_name} added successfully!")
            else:
                st.error("❌ Failed to add client.")
        st.markdown('</div>', unsafe_allow_html=True)

    # Add New Employee
    with col2:
        st.markdown('<div class="box">', unsafe_allow_html=True)
        st.markdown("### ➕ Add New Employee")
        employee_name = st.text_input("Employee Name")
        employee_email = st.text_input("Employee Email")
        employee_password = st.text_input("Employee Password", type="password")
        if st.button("Add Employee"):
            success = add_employee(employee_name, employee_email, employee_password)
            if success:
                st.success(f"✅ Employee {employee_name} added successfully!")
            else:
                st.error("❌ Failed to add employee.")
        st.markdown('</div>', unsafe_allow_html=True)

    col3, col4 = st.columns(2)

    # Project Tasks Table
    with col3:
        st.markdown('<div class="box">', unsafe_allow_html=True)
        st.subheader("📋 Project Tasks")
        tasks = get_project_tasks()
        if tasks:
            df_tasks = pd.DataFrame(tasks, columns=["Client Name", "Task Name", "Description", "Priority","Assigned Status","Due Date", "Task ID"])
            st.dataframe(df_tasks)
        else:
            st.warning("⚠️ No tasks found.")
        st.markdown('</div>', unsafe_allow_html=True)

    # Employees Table
    with col4:
        st.markdown('<div class="box">', unsafe_allow_html=True)
        st.subheader("👥 Employee List")
        employees = get_all_employees()
        if employees:
            df_employees = pd.DataFrame(employees, columns=["Employee ID", "Employee Name", "Email"])
            st.dataframe(df_employees)
        else:
            st.warning("⚠️ No employees found.")
        st.markdown('</div>', unsafe_allow_html=True)

    # Clients Table
    col5, col6 = st.columns([1, 1])
    with col5:
        st.markdown('<div class="box">', unsafe_allow_html=True)
        st.subheader("🧾 Clients List")
        clients = get_all_clients()
        if clients:
            df_clients = pd.DataFrame(clients, columns=["Client ID", "Client Name", "Email", "Phone", "Created At"])
            st.dataframe(df_clients)
        else:
            st.warning("⚠️ No clients found.")
        st.markdown('</div>', unsafe_allow_html=True)

    # Assign Task Section
    st.markdown('<div class="box">', unsafe_allow_html=True)
    st.subheader("🔗 Assign Task to Employee")

    if tasks and employees:
        col7, col8 = st.columns(2)
        with col7:
            task_ids = df_tasks["Task ID"].tolist()
            selected_task_id = st.selectbox("Select Task", task_ids)
        with col8:
            employee_ids = df_employees["Employee ID"].tolist()
            selected_employee_id = st.selectbox("Select Employee", employee_ids)

        if st.button("Assign Task"):
            success = assign_task_to_employee(selected_task_id, st.session_state.user_id, selected_employee_id)
            if success:
                st.success("✅ Task assigned successfully!")
            else:
                st.error("❌ Failed to assign task.")
    else:
        st.warning("⚠️ No tasks or employees available.")
    st.markdown('</div>', unsafe_allow_html=True)

if login_option == "Employee":
    email = st.sidebar.text_input("👤 Employee Username", "")
    password = st.sidebar.text_input("🔑 Employee Password", type="password")

    if st.sidebar.button("Login"):
        if not email:
            st.sidebar.error("❌ You can't log in. Use a @bytepx.com email.")
        else:
            admin_info = login_employee(email, password)
            if admin_info:
                st.session_state.logged_in = True
                st.session_state.user_id = admin_info["employee_id"]
                st.session_state.user_role = "employee"
                st.sidebar.success(f"✅ Logged in as Employee ({email})")
                st.rerun()
            else:
                st.sidebar.error("❌ Invalid Employee credentials!")


# Employee Panel
if st.session_state.logged_in and st.session_state.user_role == "employee":
    st.title("🧑‍💻 Employee Panel")
    st.write("🚀 You are logged in as an employee. Work tracking & task management coming soon!")

    
    st.subheader("🕓 Available Tasks to Take (Pending Task Pool)")
    pending_tasks = get_pending_tasks_for_assignment()

    if pending_tasks:
        for pending_task in pending_tasks:
            pending_task_id, task_id, task_name, description, created_at = pending_task

            with st.container():
                st.markdown(f"""
                    <div style="border:1px solid #ddd; padding: 10px; border-radius:10px; background-color: #fdfdfd; margin-bottom:10px;">
                        <strong>📌 {task_name}</strong><br>
                        📝 {description}<br>
                        ⏱️ <small>Added on: {created_at}</small>
                    </div>
                """, unsafe_allow_html=True)

                # Create a unique key for each button
                if st.button(f"Take Task", key=f"take_{pending_task_id}"):
                    success = assign_task_from_pending(pending_task_id, st.session_state.user_id)
                    if success:
                        st.success("✅ Task assigned to you successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Something went wrong. Please try again.")
    else:
        st.info("🎉 No pending tasks available right now.")


    st.subheader("📊 Employee Task Table")

    employee_task_df = get_all_employee_tasks()
    if not employee_task_df.empty:
        st.markdown("### 📝 Edit Your Task Details Below ")
        editable_columns = ["COMPLETION_DATE", "TASK_DESCRIPTION", "NO_OF_HOURS"]

        edited_df = st.data_editor(
        employee_task_df,
        use_container_width=True,
        column_config={
            "COMPLETION_DATE": st.column_config.TextColumn(),
            "TASK_DESCRIPTION": st.column_config.TextColumn(),
            "NO_OF_HOURS": st.column_config.TextColumn(),
        },
        num_rows="dynamic",
        disabled=[col for col in employee_task_df.columns if col not in editable_columns],
        key="employee_tasks_editor"
    )

    # Detect and update any changes row by row
        for idx, row in edited_df.iterrows():
            original_row = employee_task_df.loc[idx]
            has_changes = False

            for col in editable_columns:
                if str(row[col]) != str(original_row[col]):
                    has_changes = True
                    break

            if has_changes:
                update_employee_task(
                row["TASK_ID"],
                row["COMPLETION_DATE"],
                row["TASK_DESCRIPTION"],
                row["NO_OF_HOURS"]
            )
                st.toast(f"✅ Updated Task ID {row['TASK_ID']}!", icon="📝")







    st.sidebar.markdown("## 🆘 Request Help")
    with st.sidebar.form("help_form"):
        help_name = st.text_input("Your Name (for Help)")
        help_text = st.text_area("Describe your issue or request")
        submitted_help = st.form_submit_button("Submit Help Request")

        if submitted_help:
            if help_name and help_text:
                success = submit_help_request(help_name, help_text)
                if success:
                    st.sidebar.success("✅ Help request submitted!")
                else:
                    st.sidebar.error("❌ Something went wrong.")
            else:
                st.sidebar.error("❌ Please fill in both fields.")



    st.subheader("🆘 All Help Requests")

    help_requests = get_all_help_requests()

    if help_requests:
        for name, help_text in help_requests:
            with st.container():
                st.markdown(f"""
                    <div style="border:1px solid #ccc; padding: 10px; border-radius:10px; background-color: #fff3cd; margin-bottom:10px;">
                        <strong>🙋‍♂️ {name}</strong><br>
                        📝 {help_text}
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No help requests found.")




# Public Welcome Page
else:
    st.markdown('<p class="big-font">⏳ Welcome to the Time Management System</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtext">Boost your productivity by tracking and managing your time efficiently.</p>', unsafe_allow_html=True)

    # Show Current Time
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.info(f"📅 Current Time: {current_time}")

    # Footer
    st.markdown("---")
    st.markdown("📌 Coming Soon...")
