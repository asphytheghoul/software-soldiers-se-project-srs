import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import warnings
import time
import plotly.express as px
from streamlit import session_state as state

st.set_page_config(page_title='HR Analytics Dashboard', layout='wide')

warnings.filterwarnings('ignore')
st.set_option('deprecation.showPyplotGlobalUse', False)


# Load users data
users = pd.read_csv('users.csv')
users['password'] = users['password'].astype(str)

# Initialize session state
if 'logged_in' not in state:
    state.logged_in = False
    state.username = ''
    state.last_activity_time = time.time()

# Login page
if not state.logged_in:
    st.title('Login / Signup')

    username = st.text_input('Username')
    password = st.text_input('Password', type='password')

    if st.button('Login'):
        if username in users['username'].values:
            user = users[users['username'] == username].iloc[0]
            if password == user['password']:
                state.logged_in = True
                state.username = username
                state.last_activity_time = time.time()
            else:
                st.error('Incorrect password')
        else:
            st.error('Username not found')

    if st.button('Signup'):
        if username in users['username'].values:
            st.error('Username already exists')
        else:
            new_user = pd.DataFrame({'username': [username], 'password': [password]})
            users = pd.concat([users, new_user], ignore_index=True)
            users.to_csv('users.csv', index=False)
            st.success('Successfully registered')

# main page
if state.logged_in:
    if time.time() - state.last_activity_time > 10:
        state.logged_in = False
        st.warning('Session timed out. Please login again.')
        st.experimental_rerun()
    else:
        state.last_activity_time = time.time()
        st.title(f'Welcome, {state.username}')
        st.set_option('deprecation.showPyplotGlobalUse', False)

        file_path = 'employee_attrition.csv'
        data = pd.read_csv(file_path)

        data['Date of Resignation'] = pd.to_datetime(data['Date of Resignation'], errors='coerce')
        data['Resignation Quarter'] = data['Date of Resignation'].dt.quarter
        min_date = data['Date of Resignation'].min()
        max_date = data['Date of Resignation'].max()
        date_range = st.date_input('Date range', [min_date, max_date])
        start_date, end_date = pd.to_datetime(date_range)
        filtered_data = data[(data['Date of Resignation'] >= start_date) & (data['Date of Resignation'] <= end_date)]

        resignation_count = data['Year of Resignation'].notnull().sum()

        # Calculate attrition rate
        total_employees = data.shape[0]
        attrition_rate = (resignation_count / total_employees) * 100

        if attrition_rate > 80:
            st.warning('High Attrition Rate')

        # Calculate metrics
        num_employees = len(data)
        avg_age = data['Age'].mean()
        attrition = resignation_count
        attrition_rate = attrition / num_employees
        avg_salary = data['Salary'].mean()
        avg_experience = data['Experience (Years)'].mean()
        attrition_by_experience = data[data['Year of Resignation'].notnull()]['Experience (Years)'].value_counts().sort_index()
        attrition_by_salary = data[data['Year of Resignation'].notnull()]['Salary'].value_counts().sort_index()
        

        # Create Streamlit app
        st.title('HR Analytics Dashboard')
        bins = pd.interval_range(start=0, end=data['Salary'].max() + 1, freq=10000)  
        data['Salary Bin'] = pd.cut(data['Salary'], bins=bins)
        attrition_by_salary_bin = data[data['Year of Resignation'].notnull()]['Salary Bin'].value_counts().sort_index()
        attrition_by_salary_bin.index = attrition_by_salary_bin.index.astype(str)
        # Display metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f'<h1 style="color: white;">{num_employees}</h1>', unsafe_allow_html=True)
            st.caption('Number of Employees')

        with col2:
            st.markdown(f'<h1 style="color: white;">{avg_age:.2f}</h1>', unsafe_allow_html=True)
            st.caption('Average Age')

        with col3:
            st.markdown(f'<h1 style="color: white;">{attrition}</h1>', unsafe_allow_html=True)
            st.caption('Attrition')

        col4, col5, col6 = st.columns(3)

        with col4:
            st.markdown(f'<h1 style="color: white;">{attrition_rate:.2f}</h1>', unsafe_allow_html=True)
            st.caption('Attrition Rate')

        with col5:
            st.markdown(f'<h1 style="color: white;">{avg_salary:.2f}</h1>', unsafe_allow_html=True)
            st.caption('Average Salary')

        with col6:
            st.markdown(f'<h1 style="color: white;">{avg_experience:.2f}</h1>', unsafe_allow_html=True)
            st.caption('Average Years of Experience')


        # Display graphs
        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader('Attrition by Department')
            fig = px.histogram(filtered_data, x='Department', color='Department', nbins=10, template='plotly_dark')
            st.plotly_chart(fig)

        with col2:
            st.subheader('Attrition by Gender')
            fig = px.pie(filtered_data, names='Gender', template='plotly_dark')
            st.plotly_chart(fig)

        with col3:
            st.subheader('Attrition by Age')
            fig = px.pie(filtered_data, names="Age", template='plotly_dark')
            st.plotly_chart(fig)

        col4, col5, col6 = st.columns(3)

        with col4:
            st.subheader('Attrition by Experience')
            fig = px.line(attrition_by_experience, x=attrition_by_experience.index, y=attrition_by_experience.values, template='plotly_dark')
            st.plotly_chart(fig)

        with col5:
            st.subheader('Attrition by Salary')
            fig = px.line(attrition_by_salary_bin, x=attrition_by_salary_bin.index, y=attrition_by_salary_bin.values, template='plotly_dark')
            st.plotly_chart(fig)

        with col6:
            st.subheader('Attrition by Resignation Quarter')
            fig = px.histogram(filtered_data, x='Resignation Quarter', color='Resignation Quarter', nbins=10, template='plotly_dark')
            st.plotly_chart(fig)
        st.subheader('Attrition by Year')
        attrition_by_year = filtered_data['Year of Resignation'].value_counts().sort_index()
        fig = px.line(attrition_by_year, x=attrition_by_year.index, y=attrition_by_year.values, template='plotly_dark')
        st.plotly_chart(fig)

