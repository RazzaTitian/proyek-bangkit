# -*- coding: utf-8 -*-
"""Analisis.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Wsqm9WbdMe_7vIfj5CmgACMb7mQbYZeE

# Proyek Analisis Data: Air Quality Database
- **Nama:** Muhammad Razza Titian Jiwani
- **Email:** m008d4ky3036@bangkit.academy
- **ID Dicoding:** razzatitian

## Menentukan Pertanyaan Bisnis

- Across the years, which year shows the highest level of both PM2.5 and PM10?
- Is there a relevance between pollutants level and meteorological conditions on a specific period?

## Import Semua Packages/Library yang Digunakan
"""

import pandas as pd
import numpy as py
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from datetime import datetime
import csv
import streamlit as st

"""## Data Wrangling

### Gathering Data

In this part, it's pretty much just defining the file paths for ease of access. This code separates each data by the underscores.
"""

file_path = [
    'PRSA_Data_Aotizhongxin_20130301-20170228.csv',
    'PRSA_Data_Changping_20130301-20170228.csv',
    'PRSA_Data_Dingling_20130301-20170228.csv',
    'PRSA_Data_Dongsi_20130301-20170228.csv',
    'PRSA_Data_Guanyuan_20130301-20170228.csv',
    'PRSA_Data_Gucheng_20130301-20170228.csv',
    'PRSA_Data_Huairou_20130301-20170228.csv',
    'PRSA_Data_Nongzhanguan_20130301-20170228.csv',
    'PRSA_Data_Shunyi_20130301-20170228.csv',
    'PRSA_Data_Tiantan_20130301-20170228.csv',
    'PRSA_Data_Wanliu_20130301-20170228.csv',
    'PRSA_Data_Wanshouxigong_20130301-20170228.csv'
]

data_frames = {name.split('_')[2]: pd.read_csv(name) for name in file_path}

#Uncomment this line to check if the above code works
#check = list(data_frames.keys())[0]
#data_frames[check].head()

"""### Assessing Data

Here, we will assess the data. Is there any missing numbers? What data types are there? Any duplicates? These are valid questions one must be aware of, considering the implication. I gave the summary for ease of reading. Next step, of course, is to eliminate (if any) the missing numbers and duplicates. Why the f? It's format. Formatted string. Helps with variable-inserted string.
"""

for station, df in data_frames.items():
    print(f"--- {station} Station ---")
    # Checks missingno
    # Pokemon reference, I know
    print("Missing:")
    print(df.isnull().sum())
    print("\n")

    # Gives the data types of each station
    print("Data Types:")
    print(df.dtypes)
    print("\n")

    # Look for duplicates
    duplicates = df.duplicated().sum()
    print(f"Number of duplicates: {duplicates}")
    print("\n")

    # Provide summary
    print("Summary:")
    print(df.describe())
    print("\n\n")

"""### Cleaning Data"""

def outliers(df, column):

    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    df[column] = df[column].apply(lambda x: df[column].median() if x < lower_bound or x > upper_bound else x)

def clean_air_quality_data(df):

    # Handle missing values
    for col in ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']:
        df[col].fillna(df[col].median(), inplace=True)

    # Convert date and time
    df['date_time'] = pd.to_datetime(df[['year', 'month', 'day', 'hour']])
    df.drop(['year', 'month', 'day', 'hour'], axis=1, inplace=True)

    # Impute wind direction
    if 'wd' in df.columns:
        df['wd'] = df['wd'].fillna(df['wd'].mode()[0])

    # Drop duplicates
    df.drop_duplicates(inplace=True)

    # Outlier handling
    pollutants = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']
    for pollutant in pollutants:
        outliers(df, pollutant)

    return df

for station in data_frames:
    data_frames[station] = clean_air_quality_data(data_frames[station])

"""## Exploratory Data Analysis (EDA)

### Explore ...

**We're checking the data for things that might help us answer the questions listed above, e.g. PM levels**
"""

for station, df in data_frames.items():
    plt.figure(figsize=(10, 5))
    sns.histplot(df['PM2.5'], bins=50, kde=True)
    plt.title(f'Distribution of PM2.5 levels at {station} Station')
    plt.xlabel('(PM2.5 (µg/m³)')
    plt.ylabel('Frequency')
    plt.show()

for station, df in data_frames.items():
    plt.figure(figsize=(10, 5))
    sns.histplot(df['PM10'], bins=50, kde=True)
    plt.title(f'Distribution of PM10 levels at {station} Station')
    plt.xlabel('PM10 (µg/m³)')
    plt.ylabel('Frequency')
    plt.show()

"""**We make a correlation matrix to see if there is substantial evidence for question number 2**"""

plt.figure(figsize=(12, 10))
sns.heatmap(data_frames[first_station].corr(), annot=True, fmt='.2f', cmap='coolwarm')
plt.title('Correlation Matrix of Variables')
plt.show()

"""## Visualization & Explanatory Analysis

### Pertanyaan 1:

This is a monthly average for the PM levels to see which year has the highest PM level.
"""

def plot_monthly_average(data_frames, pollutant):
    if pollutant not in ['PM2.5', 'PM10']:
        raise ValueError("That's a negatory, it's a fake pollutant")

    plt.figure(figsize=(15, 7))

    for station, df in data_frames.items():
        if 'month_year' not in df.columns:
            df['month_year'] = df['date_time'].dt.to_period('M')

        monthly_avg = df.groupby('month_year')[pollutant].mean().sort_index()
        sns.lineplot(x=monthly_avg.index.to_timestamp(), y=monthly_avg.values, label=station)

    plt.title(f'Monthly Average {pollutant} Levels Across All Stations')
    plt.xlabel('Month/Year')
    plt.ylabel(f'Average {pollutant} (µg/m³)')
    plt.legend(title='Stations')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

plot_monthly_average(data_frames, 'PM2.5')
plot_monthly_average(data_frames, 'PM10')

"""### Pertanyaan 2:

Feel free to change the parameter. It's date and the scatterplot. This shows correlation between two parameters, as requested by the 2nd question.
"""

specific_period_df = data_frames[first_station][(data_frames[first_station]['date_time'] >= '2015-01') & (data_frames[first_station]['date_time'] < '2015-12')]

sns.scatterplot(data=specific_period_df, x='TEMP', y='PM2.5')
plt.title('Correlation between Temperature and PM2.5 for January 2015')
plt.xlabel('Temperature (°C)')
plt.ylabel('PM2.5 (µg/m³)')
plt.show()

correlation = specific_period_df['TEMP'].corr(specific_period_df['PM2.5'])
print(f"The correlation coefficient between temperature and PM2.5 for January 2015 is: {correlation}")

"""## Conclusion

- It is evident that, in 2013, PM2.5 are at the highest, and in 2014, PM10 is the highest
- There is correlation between pollutants and the PM level on every yearly scale

# Glossary

*   PM = Particulate Matter (in μg/m3)
"""
