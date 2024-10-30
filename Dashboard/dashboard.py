import pandas as pd
import streamlit as st
import matplotlib as plt
import seaborn as sns
from babel.numbers import format_currency
sns.set(style="darkgrid")

# Load data
all_df = pd.read_csv("all_data.csv")

# Create the function
def create_weekday_analysis_df(all_df):
    weekday_analysis_df = all_df.groupby('weekday').agg({
        'cnt': 'mean',
        'casual': 'mean',
        'registered': 'mean'
    }).reset_index()
    return weekday_analysis_df

def create_workingday_analysis_df(all_df):
    workingday_analysis_df = all_df.groupby('workingday').agg({
        'cnt': 'mean',
        'casual': 'mean',
        'registered': 'mean'
    }).reset_index()
    return workingday_analysis_df

def create_avg_rentals_df(all_df):
    avg_rentals_df = all_df.groupby('workingday')['cnt'].mean().reset_index()
    avg_rentals_df.rename(columns={'cnt': 'avg_rentals'}, inplace=True)
    return avg_rentals_df

def create_monthly_trend_df(all_df):
    all_df['dteday'] = pd.to_datetime(all_df['dteday'])
    all_df['year_month'] = all_df['dteday'].dt.to_period('M').astype(str)
    monthly_trend_df = all_df.groupby(['year_month', 'is_weekday']).agg({'cnt': 'mean'}).reset_index()
    monthly_trend_df.rename(columns={'cnt': 'total_rentals'}, inplace=True)
    return monthly_trend_df

def create_monthly_data_df(all_df):
    monthly_data_df = all_df.resample(rule='M', on='dteday').agg({
        "cnt": "sum",   
        "casual": "sum", 
        "registered": "sum"  
    })

    monthly_data_df.index = monthly_data_df.index.strftime('%Y-%m')  
    monthly_data_df = monthly_data_df.reset_index() 

    monthly_data_df.rename(columns={
        "cnt": "total_rentals",
        "casual": "casual_rentals",
        "registered": "registered_rentals"  
    }, inplace=True)

    return monthly_data_df

# Sort and reset index for date columns
datetime_column = ['dteday']
all_df.sort_values(by='dteday', inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_column:
    all_df[column] = pd.to_datetime(all_df[column])

# Create filter component
min_date = all_df["dteday"].min()
max_date = all_df["dteday"].max()

with st.sidebar:
    start_date, end_date = st.date_input(
        label='Time Range', min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Filter data based on selected date range
main_df = all_df[(all_df['dteday'] >= str(start_date)) & (all_df['dteday'] <= str(end_date))]

# Prepare DataFrames
monthly_data_df = create_monthly_data_df(main_df)
weekday_analysis_df = create_weekday_analysis_df(main_df)
workingday_analysis_df = create_workingday_analysis_df(main_df)
avg_rentals_df = create_avg_rentals_df(main_df)
monthly_trend_df = create_monthly_trend_df(main_df)

# Dashboard Visualization
st.header("Dashboard of Bike Sharing Data")

# Plot for Monthly Data
st.subheader("Monthly Orders")
plt.figure(figsize=(12, 6))
monthly_data_df.set_index('dteday')['total_rentals'].plot(kind='bar')
plt.title('Average Monthly Bike Rentals')
plt.xlabel('Month')
plt.ylabel('Total Rentals')
plt.xticks(rotation=45)  
plt.tight_layout()

# Show the plot in Streamlit
st.pyplot(plt)

# Plot for Weekday Analysis
st.subheader("Weekday Analysis")
plt.figure(figsize=(10, 5))
weekday_analysis_df.plot(x='weekday', y=['casual', 'registered'], kind='bar', ax=plt.gca())
plt.title('Average Rentals by Weekday')
plt.ylabel('Average Rentals')
plt.xticks(ticks=range(7), labels=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], rotation=0)
plt.tight_layout()

# Show the plot in Streamlit
st.pyplot(plt)

# Plot for Working Day Analysis
st.subheader("Working Day Analysis")

# Set image size
plt.figure(figsize=(10, 6))

# Using DataFrame to create a bar chart
workingday_analysis_df.set_index('workingday')[['casual', 'registered']].plot(kind='bar', alpha=0.7, ax=plt.gca())

# Add titles and labels
plt.title('Average User Count by Working Day')
plt.xlabel('Working Day')
plt.xticks(ticks=range(2), labels=['Not Working Day', 'Working Day'], rotation=0)
plt.ylabel('Average User Count')

# Show legend
plt.legend(title='User Type')

# Display plot
plt.tight_layout()

# Show the plot in Streamlit
st.pyplot(plt)

# Plot for Average Rentals
avg_rentals_df = main_df.groupby('workingday')['cnt'].mean().reset_index()

# Add subheader
st.subheader("Average Rentals on Working Days vs Weekends")

# Create the plot
fig4, ax4 = plt.subplots(figsize=(8, 6))
sns.barplot(data=avg_rentals_df, x='workingday', y='cnt', ax=ax4)  
ax4.set_title('Comparison of Average Bike Rentals\nWorking Days vs Weekends', fontsize=16)
ax4.set_xlabel('Working Day (0 = Weekend, 1 = Working Day)', fontsize=12)
ax4.set_ylabel('Average Bike Rentals', fontsize=12)

# Show the plot in Streamlit
plt.tight_layout()
st.pyplot(fig4)

# Create a monthly trend plot
st.subheader("Monthly Trend Data")
fig5, ax5 = plt.subplots(figsize=(10, 6))
sns.lineplot(data=monthly_trend_df, x='year_month', y='total_rentals', hue='is_weekday', ax=ax5)
ax5.set_title('Total Rentals Trend Over Months', fontsize=16)
ax5.set_xlabel('Year-Month', fontsize=12)
ax5.set_ylabel('Total Rentals', fontsize=12)
ax5.grid(True)

# Show the plot in Streamlit
plt.xticks(rotation=45)
st.pyplot(fig5)
