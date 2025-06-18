import streamlit as st
import requests

# ✅ Replace with your actual deployed FastAPI backend
API_URL = "https://your-fastapi-service.onrender.com"

st.set_page_config(page_title="Calculator App", layout="centered")

# Session state for auth
if "token" not in st.session_state:
    st.session_state.token = None


# ------------------ AUTH ------------------

def register():
    st.title("🔐 Register")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Register"):
        try:
            res = requests.post(f"{API_URL}/register", json={"username": username, "password": password})
            res.raise_for_status()
            st.success("✅ Registered successfully! Now log in.")
        except requests.exceptions.HTTPError:
            try:
                st.error(res.json().get("detail", "Something went wrong."))
            except:
                st.error(f"Error: {res.text}")
        except requests.exceptions.ConnectionError:
            st.error("❌ Could not connect to API. Check your API_URL.")


def login():
    st.title("🔐 Login")
    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")
    if st.button("Login"):
        try:
            res = requests.post(f"{API_URL}/login", data={"username": username, "password": password})
            res.raise_for_status()
            st.session_state.token = res.json()["access_token"]
            st.success("✅ Login successful!")
        except requests.exceptions.HTTPError:
            try:
                st.error(res.json().get("detail", "Login failed."))
            except:
                st.error(f"Error: {res.text}")
        except requests.exceptions.ConnectionError:
            st.error("❌ Could not connect to API. Check your API_URL.")


# ------------------ CALCULATOR ------------------

def calculator():
    st.title("🧮 Calculator")

    num1 = st.number_input("Enter first number")
    num2 = st.number_input("Enter second number")
    operation = st.selectbox("Select operation", ["add", "subtract", "multiply", "divide"])

    if st.button("Calculate"):
        if not st.session_state.token:
            st.warning("⚠️ Please login first.")
            return

        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        payload = {"num1": num1, "num2": num2, "operation": operation}

        try:
            res = requests.post(f"{API_URL}/calculate", json=payload, headers=headers)
            res.raise_for_status()
            result = res.json()["result"]
            st.success(f"✅ Result: {result}")
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Error: {e}")


# ------------------ HISTORY ------------------

def view_history():
    st.title("📜 Calculation History")

    if not st.session_state.token:
        st.warning("⚠️ Please login first.")
        return

    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    try:
        res = requests.get(f"{API_URL}/history", headers=headers)
        res.raise_for_status()
        history = res.json()
        for item in history:
            st.write(f"{item['operation'].capitalize()} of {item['num1']} and {item['num2']} = {item['result']}")
    except:
        st.error("❌ Failed to fetch history.")


# ------------------ MAIN ------------------

st.sidebar.title("📋 Menu")
choice = st.sidebar.radio("Go to", ["Login", "Register", "Calculator", "History", "Logout"])

if choice == "Register":
    register()
elif choice == "Login":
    login()
elif choice == "Calculator":
    calculator()
elif choice == "History":
    view_history()
elif choice == "Logout":
    st.session_state.token = None
    st.success("✅ Logged out!")

