import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from datetime import datetime

# Set visualization style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

# Load the dataset
try:
    covid_df = pd.read_csv('owid-covid-data.csv')
    print("Dataset loaded successfully!")
except FileNotFoundError:
    print("Error: File not found. Please download the dataset and ensure it's in your working directory.")
    # For demonstration, we'll load from URL if local file not found
    url = "https://covid.ourworldindata.org/data/owid-covid-data.csv"
    covid_df = pd.read_csv(url)
    print("Loaded dataset directly from Our World in Data website")

# Initial exploration
print("\nDataset shape:", covid_df.shape)
print("\nFirst 5 rows:")
print(covid_df.head())

print("\nColumns in dataset:")
print(covid_df.columns.tolist())

print("\nMissing values per column:")
print(covid_df.isnull().sum().sort_values(ascending=False).head(20))

# Convert date column to datetime
covid_df['date'] = pd.to_datetime(covid_df['date'])

# Select countries of interest
countries = ['Kenya', 'United States', 'India', 'Brazil', 'Germany', 'South Africa']
filtered_df = covid_df[covid_df['location'].isin(countries)].copy()

# Handle missing values - we'll fill forward for time-series data
cols_to_fill = ['total_cases', 'total_deaths', 'total_vaccinations', 'people_vaccinated']
for col in cols_to_fill:
    filtered_df[col] = filtered_df.groupby('location')[col].ffill()

# Calculate important metrics
filtered_df['death_rate'] = filtered_df['total_deaths'] / filtered_df['total_cases']
filtered_df['vaccination_rate'] = filtered_df['people_vaccinated'] / filtered_df['population']

# Drop rows where essential metrics are still missing
filtered_df = filtered_df.dropna(subset=['total_cases', 'total_deaths', 'date'])

print("\nCleaned dataset sample:")
print(filtered_df[['date', 'location', 'total_cases', 'total_deaths', 'people_vaccinated']].head())

# Create a figure with multiple subplots
plt.figure(figsize=(18, 12))

# 1. Total cases over time
plt.subplot(2, 2, 1)
for country in countries:
    country_data = filtered_df[filtered_df['location'] == country]
    plt.plot(country_data['date'], country_data['total_cases'], label=country)
plt.title('Total COVID-19 Cases Over Time')
plt.xlabel('Date')
plt.ylabel('Total Cases')
plt.legend()

# 2. Total deaths over time
plt.subplot(2, 2, 2)
for country in countries:
    country_data = filtered_df[filtered_df['location'] == country]
    plt.plot(country_data['date'], country_data['total_deaths'], label=country)
plt.title('Total COVID-19 Deaths Over Time')
plt.xlabel('Date')
plt.ylabel('Total Deaths')
plt.legend()

# 3. New cases comparison (7-day rolling average)
plt.subplot(2, 2, 3)
for country in countries:
    country_data = filtered_df[filtered_df['location'] == country]
    # Calculate 7-day moving average for smoother visualization
    country_data['new_cases_smoothed'] = country_data['new_cases'].rolling(7).mean()
    plt.plot(country_data['date'], country_data['new_cases_smoothed'], label=country)
plt.title('Daily New Cases (7-day average)')
plt.xlabel('Date')
plt.ylabel('New Cases')
plt.legend()

# 4. Death rate comparison
plt.subplot(2, 2, 4)
for country in countries:
    country_data = filtered_df[filtered_df['location'] == country]
    plt.plot(country_data['date'], country_data['death_rate'], label=country)
plt.title('Case Fatality Rate Over Time')
plt.xlabel('Date')
plt.ylabel('Death Rate (Deaths/Cases)')
plt.legend()

plt.tight_layout()
plt.show()

# Top countries analysis (from full dataset)
latest_data = covid_df[covid_df['date'] == covid_df['date'].max()]
top_countries_cases = latest_data.sort_values('total_cases_per_million', ascending=False).head(10)

plt.figure(figsize=(12, 6))
sns.barplot(x='total_cases_per_million', y='location', data=top_countries_cases, palette='viridis')
plt.title('Top 10 Countries by Total Cases per Million')
plt.xlabel('Cases per Million People')
plt.ylabel('Country')
plt.show()

# Vaccination analysis
plt.figure(figsize=(18, 6))

# 1. Total vaccinations over time
plt.subplot(1, 2, 1)
for country in countries:
    country_data = filtered_df[filtered_df['location'] == country]
    plt.plot(country_data['date'], country_data['total_vaccinations'], label=country)
plt.title('Total Vaccinations Over Time')
plt.xlabel('Date')
plt.ylabel('Total Vaccinations')
plt.legend()

# 2. Vaccination rate (% population)
plt.subplot(1, 2, 2)
for country in countries:
    country_data = filtered_df[filtered_df['location'] == country]
    plt.plot(country_data['date'], country_data['vaccination_rate'], label=country)
plt.title('Vaccination Rate (% Population) Over Time')
plt.xlabel('Date')
plt.ylabel('Vaccination Rate')
plt.legend()

plt.tight_layout()
plt.show()

# Latest vaccination status pie chart
latest_vaccines = filtered_df[filtered_df['date'] == filtered_df['date'].max()]
plt.figure(figsize=(8, 8))
plt.pie(latest_vaccines['people_vaccinated'], 
        labels=latest_vaccines['location'], 
        autopct='%1.1f%%',
        colors=sns.color_palette('pastel'))
plt.title('Distribution of Vaccinated People Among Selected Countries')
plt.show()

# Choropleth map of total cases per million
latest_global = covid_df[covid_df['date'] == covid_df['date'].max()]

fig = px.choropleth(latest_global, 
                    locations="iso_code",
                    color="total_cases_per_million",
                    hover_name="location",
                    color_continuous_scale=px.colors.sequential.Plasma,
                    title="Global COVID-19 Cases per Million People",
                    range_color=(0, 200000))
fig.show()

# Choropleth map of vaccination rates
fig = px.choropleth(latest_global, 
                    locations="iso_code",
                    color="people_vaccinated_per_hundred",
                    hover_name="location",
                    color_continuous_scale=px.colors.sequential.Viridis,
                    title="Global COVID-19 Vaccinations per 100 People",
                    range_color=(0, 100))
fig.show()
