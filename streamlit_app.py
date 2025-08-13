import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ---------------- Paths ----------------
DATA_PATH = r"D:\Projects\Customer_Due_Tracker_System\backend\data"
FILES = {
    "customers": "customers.csv",
    "added": "added_customers.csv",
    "deleted": "deleted_customers.csv",
    "dues": "dues.csv",
    "logs": "logs.csv"
}
FILES = {k: os.path.join(DATA_PATH, v) for k, v in FILES.items()}

# ---------------- Page Config ----------------
st.set_page_config(layout="wide")
st.title("Customer Due Tracker System")

# ---------------- Helper Functions ----------------
def load_csv(file, cols=None):
    return pd.read_csv(file) if os.path.exists(file) else pd.DataFrame(columns=cols or [])

def save_csv(df, file):
    os.makedirs(DATA_PATH, exist_ok=True)
    df.to_csv(file, index=False)

def log_action(action, details=""):
    entry = pd.DataFrame([{
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": action,
        "details": details
    }])
    save_csv(pd.concat([load_csv(FILES['logs']), entry], ignore_index=True), FILES['logs'])

def save_due(customer):
    entry = pd.DataFrame([{
        "id": customer['id'],
        "name": customer['name'],
        "due": customer['due'],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }])
    save_csv(pd.concat([load_csv(FILES['dues']), entry], ignore_index=True), FILES['dues'])

def append_csv(file, customer):
    df = load_csv(file, customer.keys())
    df = pd.concat([df, pd.DataFrame([customer])], ignore_index=True)
    save_csv(df, file)

def load_customers():
    cols = ['id','name','phone','email','address','due','last_update','status']
    df = load_csv(FILES['customers'], cols)
    df['id'] = pd.to_numeric(df.get('id', pd.Series(dtype=int)), errors='coerce')
    df['due'] = pd.to_numeric(df.get('due', pd.Series(dtype=float)), errors='coerce')
    for col in ['name','phone','email','address','status','last_update']:
        df[col] = df.get(col, '').fillna('').astype(str)
    return df

def get_next_id(df):
    return int(df['id'].max() + 1) if not df.empty else 1

# ---------------- Sidebar Tabs ----------------
tabs = {
    "➕ Add Customer": "add",
    "🗑️ Delete Customer": "delete",
    "📋 View All Customers": "view"
}

st.session_state.setdefault("tab", list(tabs.keys())[0])
for t in tabs: st.sidebar.button(t, use_container_width=True, on_click=lambda tab=t: st.session_state.update({"tab": tab}))
choice = st.session_state.tab

# ---------------- Tab Logic ----------------
if choice == "➕ Add Customer":
    st.header("Add Customer")
    name = st.text_input("Name").strip()
    phone = st.text_input("Phone").strip()
    email = st.text_input("Email").strip()
    address = st.text_input("Address").strip()
    due = st.number_input("Due Amount", min_value=0.0, format="%.2f")

    if st.button("Add Customer"):
        df = load_customers()
        new_id = get_next_id(df)
        cust = {"id": new_id, "name": name, "phone": phone, "email": email,
                "address": address, "due": due,
                "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "active"}
        # Save to customers, added, dues, logs
        save_csv(pd.concat([df, pd.DataFrame([cust])], ignore_index=True), FILES['customers'])
        append_csv(FILES['added'], cust)
        save_due(cust)
        log_action("Add Customer", f"Added {name}, ID={new_id}, Due={due}")
        st.success(f"Customer '{name}' added successfully!")

elif choice == "🗑️ Delete Customer":
    st.header("Delete Customer")
    df = load_customers()
    if df.empty:
        st.info("No customers available.")
    else:
        option = st.radio("Delete Option:", ["Single Customer", "All Customers"])
        if option == "Single Customer":
            cust_id = st.number_input("Customer ID", min_value=1, step=1)
            if cust_id in df['id'].values and st.button("Delete Customer"):
                cust = df[df['id']==cust_id].iloc[0].to_dict()
                df = df[df['id'] != cust_id]
                save_csv(df, FILES['customers'])
                append_csv(FILES['deleted'], cust)
                save_due(cust)
                log_action("Delete Customer", f"Deleted {cust['name']}, ID={cust_id}, Due={cust['due']}")
                st.success(f"Customer '{cust['name']}' deleted!")

        else:  # Delete all
            if st.button("Delete All"):
                all_customers = df.copy()
                save_csv(pd.DataFrame(columns=df.columns), FILES['customers'])
                for _, cust in all_customers.iterrows(): 
                    append_csv(FILES['deleted'], cust.to_dict())
                    save_due(cust.to_dict())
                log_action("Delete All Customers", f"Deleted all {len(all_customers)} customers")
                st.success(f"All {len(all_customers)} customers deleted!")

elif choice == "📋 View All Customers":
    st.header("All Customers")
    df = load_customers()
    if df.empty:
        st.info("No customers found.")
    else:
        st.dataframe(df)
