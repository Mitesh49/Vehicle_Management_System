import streamlit as st
import pandas as pd
import os

# Function to check if user exists in the login database
def user_exists(username):
    if os.path.exists("login.xlsx"):
        try:
            login_df = pd.read_excel("login.xlsx")
            return username in login_df['Username'].values
        except FileNotFoundError:
            return False
    else:
        return False

# Function to validate login credentials
def validate_login(username, password):
    if os.path.exists("login.xlsx"):
        try:
            login_df = pd.read_excel("login.xlsx")
            user_row = login_df[login_df['Username'] == username]
            if len(user_row) == 0:
                return False
            return user_row.iloc[0]['Password'] == password
        except FileNotFoundError:
            return False
    else:
        return False

# Function to add user signup details
def add_user(username, password):
    if os.path.exists("login.xlsx"):
        login_df = pd.read_excel("login.xlsx")
        new_user = pd.DataFrame({'Username': [username], 'Password': [password]})
        login_df = pd.concat([login_df, new_user], ignore_index=True)
        login_df.to_excel("login.xlsx", index=False)
    else:
        new_user = pd.DataFrame({'Username': [username], 'Password': [password]})
        new_user.to_excel("login.xlsx", index=False)

# Function to add vehicle maintenance record
def add_maintenance_record(vehicle_id, last_maintenance_date, next_maintenance_date):
    if os.path.exists("data.xlsx"):
        data_df = pd.read_excel("data.xlsx")
        status = 'Upcoming' if pd.Timestamp(next_maintenance_date) > pd.Timestamp.now() else 'Overdue'
        new_record = pd.DataFrame({'Vehicle ID': [vehicle_id],
                                   'Last Maintenance Date': [last_maintenance_date],
                                   'Next Maintenance Date': [next_maintenance_date],
                                   'Status': [status]})
        data_df = pd.concat([data_df, new_record], ignore_index=True)
        data_df.to_excel("data.xlsx", index=False)
    else:
        status = 'Upcoming' if pd.Timestamp(next_maintenance_date) > pd.Timestamp.now() else 'Overdue'
        new_record = pd.DataFrame({'Vehicle ID': [vehicle_id],
                                   'Last Maintenance Date': [last_maintenance_date],
                                   'Next Maintenance Date': [next_maintenance_date],
                                   'Status': [status]})
        new_record.to_excel("data.xlsx", index=False)


# Signup page
def signup():
    st.title('Signup')
    username = st.text_input('Username', key='signup_username')
    password = st.text_input('Password', type='password', key='signup_password')
    confirm_password = st.text_input('Confirm Password', type='password', key='signup_confirm_password')
    if password != confirm_password:
        st.warning('Passwords do not match!')
        return
    if st.button('Signup'):
        if user_exists(username):
            st.error('Username already exists!')
            return
        add_user(username, password)
        st.success('Signup successful! Please login.')
        st.write("[Login](#login)")

# Login page
def login():
    st.title('Login')
    username = st.text_input('Username', key='login_username')
    password = st.text_input('Password', type='password', key='login_password')
    if st.button('Login'):
        if validate_login(username, password):
            st.success('Login successful!')
            st.session_state.logged_in = True
            st.session_state.username = username
        else:
            st.error('Invalid username or password!')

# Sorting function
def sort_by_status(df):
    df['Next Maintenance Date'] = pd.to_datetime(df['Next Maintenance Date'])
    df.sort_values(by='Next Maintenance Date', inplace=True)
    return df

# Main page with vehicle maintenance records
def main_page():
    st.title('Main Page')
    st.write(f"Welcome, {st.session_state.username}!")
    
    st.subheader('Add Maintenance Record')
    vehicle_id = st.text_input('Vehicle ID', key='vehicle_id')
    last_maintenance_date = st.date_input('Last Maintenance Date', key='last_maintenance_date')
    next_maintenance_date = st.date_input('Next Maintenance Date', key='next_maintenance_date')
    if st.button('Add Record', key='add_record'):
        add_maintenance_record(vehicle_id, last_maintenance_date, next_maintenance_date)
        st.success('Record added successfully!')
    
    st.subheader('Maintenance Records')
    sort_option = st.radio("Sort by:", ("All", "Upcoming", "Overdue"))
    if os.path.exists("data.xlsx"):
        data_df = pd.read_excel("data.xlsx")
        if sort_option == "All":
            st.write(data_df)
        elif sort_option == "Upcoming":
            data_df = sort_by_status(data_df)
            upcoming_df = data_df[data_df['Next Maintenance Date'] > pd.Timestamp.now()]
            st.write(upcoming_df)
        elif sort_option == "Overdue":
            data_df = sort_by_status(data_df)
            overdue_df = data_df[data_df['Next Maintenance Date'] < pd.Timestamp.now()]
            st.write(overdue_df)
    else:
        st.write("No maintenance records found.")

# Display login or signup based on user choice
option = st.radio("Choose an action:", ("Login", "Signup"))

if option == "Signup":
    signup()
elif option == "Login":
    login()
    
if getattr(st.session_state, 'logged_in', False):
    main_page()
