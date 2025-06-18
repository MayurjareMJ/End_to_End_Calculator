### ✅ File: app.py (Streamlit Frontend with Login/Register + History)
import streamlit as st
import requests

st.set_page_config(page_title="FastAPI Calculator", layout="centered")
st.title("🧮 Secure Calculator with Login")

API_URL = "http://localhost:8000"

if "token" not in st.session_state:
    st.session_state.token = None
    st.session_state.username = ""

# Login/Register
st.sidebar.header("🔐 Authentication")
auth_mode = st.sidebar.radio("Mode", ["Login", "Register"])
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

if st.sidebar.button(auth_mode):
    if auth_mode == "Register":
        res = requests.post(f"{API_URL}/register", json={"username": username, "password": password})
        if res.status_code == 200:
            st.success("Registered successfully! Please login.")
        else:
            st.error(res.json().get("detail"))
    else:
        data = {"username": username, "password": password}
        res = requests.post(f"{API_URL}/token", data=data)
        if res.status_code == 200:
            st.session_state.token = res.json()["access_token"]
            st.session_state.username = username
            st.success("Logged in successfully!")
        else:
            st.error("Invalid credentials")

if st.session_state.token:
    st.success(f"Logged in as: {st.session_state.username}")

    num1 = st.number_input("Enter first number", key="num1")
    num2 = st.number_input("Enter second number", key="num2")
    operation = st.selectbox("Choose operation", ["add", "subtract", "multiply", "divide"])

    if st.button("Calculate"):
        payload = {"num1": num1, "num2": num2, "operation": operation}
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        res = requests.post(f"{API_URL}/calculate", json=payload, headers=headers)
        if res.status_code == 200:
            st.success(f"✅ Result: {res.json()['result']}")
        else:
            st.error(f"❌ {res.json().get('detail')}")

    if st.button("Show History"):
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        res = requests.get(f"{API_URL}/history", headers=headers)
        if res.status_code == 200:
            st.subheader("📋 Calculation History")
            for row in res.json():
                st.write(f"{row['num1']} {row['operation']} {row['num2']} = {row['result']}")
        else:
            st.error("Could not fetch history")