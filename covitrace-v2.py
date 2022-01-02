# uncomment below lines of code to install required packages
# !pip install streamlit
# !pip install pandas
# !pip install numpy
# !pip install datetime
# !pip install plotly_express

import streamlit as st
import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

@st.cache
def fetch_vaccination():
    url = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv'
    df = pd.read_csv(url)
    df['date'] = pd.to_datetime(df['date']).dt.date
    return df
    
df = fetch_vaccination()

today = date.today().strftime("%d %b, %Y")

st.title("covitrace - 1.5")
st.write('## Welcome to the Covid Vaccination Analysis')
st.caption('Check the sidebar options (top-left arrow to be clicked, if sidebar is not visible)')
st.write('### Created by Vinay Babu')
st.write('''The covitrace is a tool designed using Python and Streamlit to analyse covid vacinnation.''')

st.sidebar.title("Covid Vaccination Analysis")

if st.sidebar.checkbox('Raw data as on '+today):
    df
        
    # data downloading as 'csv'
    @st.cache
    def convert_df(df):
        return df.to_csv().encode('utf-8')
    
    csv = convert_df(df)
    
    st.download_button(
   "Press to download data",
   csv,
   "file.csv",
   "text/csv",
   key='download1-csv'
    )

if st.sidebar.checkbox('Date filter'):
    N_DAYS = 30 # set for '30' days; may be changed for the default view
    start = datetime.now() - timedelta(days=N_DAYS)
    end = datetime.now()
    
    start_date = st.sidebar.date_input('Start date (default set for 30 days back)', start)
    end_date = st.sidebar.date_input('End date (default set for today)', end) 
    if start_date < end_date:
        pass
        mask = (df['date'] >= start_date) & (df['date'] <= end_date)
        df = df.loc[mask]
    else:
        st.error('Error: End date should be chosen after the start day.')
    
sub_df=df[["location","date", "people_vaccinated", "people_vaccinated_per_hundred", "people_fully_vaccinated", "people_fully_vaccinated_per_hundred"]]

if st.sidebar.checkbox('Vacinnations progress (global)'):
    sub_df
        
    # data downloading as 'csv'
    @st.cache
    def convert_df(sub_df):
        return sub_df.to_csv().encode('utf-8')
    
    csv = convert_df(sub_df)
    
    st.download_button(
   "Press to download data",
   csv,
   "file.csv",
   "text/csv",
   key='download2-csv'
    )
    
    with st.expander("Click here to see top and poor performers as on "+today):
    
        # top and bottom 10 entries of 'people_vaccinated_per_hundred'
        perform_people_vaccinated_per_hundred=sub_df.sort_values('people_vaccinated_per_hundred', ascending=False).drop_duplicates(['location']).drop(["people_vaccinated", "people_fully_vaccinated", "people_fully_vaccinated_per_hundred"], axis = 1)

        if st.checkbox('Top 10 locations based on people vaccinated per hundred'):
            st.write(perform_people_vaccinated_per_hundred.head(10))
        if st.checkbox('Bottom 10 locations based on people vaccinated per hundred'):
            st.write(perform_people_vaccinated_per_hundred.tail(10))        

        # top and bottom 10 entries of 'people_fully_vaccinated_per_hundred'
        perform_people_fully_vaccinated_per_hundred=sub_df.sort_values('people_fully_vaccinated_per_hundred', ascending=False).drop_duplicates(['location']).drop(["people_vaccinated","people_vaccinated_per_hundred", "people_fully_vaccinated"], axis = 1)

        if st.checkbox('Top 10 locations based on people fully vaccinated per hundred'):            
            st.write(perform_people_fully_vaccinated_per_hundred.head(10))
        if st.checkbox('Bottom 10 locations based on people fully vaccinated per hundred'):            
            st.write(perform_people_fully_vaccinated_per_hundred.tail(10))

        # Vacinnations progress (countrywise)     
if st.sidebar.checkbox('Vacinnations progress (countrywise)'):
    # selection of country from 'location'
    country = st.selectbox("Select the country: ", sub_df['location'].unique())
    sub_df_country = sub_df.loc[sub_df['location'] == country].sort_values(by='date', ascending=False)
    sub_df_country
    
    with st.expander("Click here for the vacinnation status as on "+today):
        # display of latest figure of vacinnation
        people_vaccinated = sub_df_country['people_vaccinated'].iloc[0]
        people_vaccinated_per_hundred = sub_df_country['people_vaccinated_per_hundred'].iloc[0]
        people_fully_vaccinated = sub_df_country['people_fully_vaccinated'].iloc[0]
        people_fully_vaccinated_per_hundred = sub_df_country['people_fully_vaccinated_per_hundred'].iloc[0]
        st.write('People vaccinated in '+country, 'are', people_vaccinated)
        st.write('People vaccinated per hundred in '+country, 'are', people_vaccinated_per_hundred)
        st.write('People fully vaccinated in '+country, 'are', people_fully_vaccinated)
        st.write('People fully vaccinated per hundred in '+country, 'are', people_fully_vaccinated_per_hundred)
    
    # data downloading as 'csv'
    @st.cache
    def convert_df(sub_df_country):
        return sub_df_country.to_csv().encode('utf-8')
    
    csv = convert_df(sub_df_country)
    
    st.download_button(
   "Press to download data",
   csv,
   "file.csv",
   "text/csv",
   key='download3-csv'
    )    
    
    if st.checkbox('Show/Hide graph of people vaccinated and people fully vaccinated'):
        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        # Add traces
        fig.add_trace(
            go.Scatter(x=sub_df_country['date'], y=sub_df_country['people_vaccinated'], name="people_vaccinated"),
            secondary_y=False,
        )
        
        fig.add_trace(
            go.Scatter(x=sub_df_country['date'], y=sub_df_country['people_fully_vaccinated'], name="people_fully_vaccinated"),
            secondary_y=True,
        )

        # Add figure title
        fig.update_layout(
            title_text="People vaccinated & People fully vaccinated of " +country
        )
        # Set y-axes titles
        fig.update_yaxes(title_text="people_vaccinated", secondary_y=False)
        fig.update_yaxes(title_text="people_fully_vaccinated", secondary_y=True)
        
        st.plotly_chart(fig, use_container_width=True)
        
    if st.checkbox('Show/Hide graph of people vaccinated per hundred and people fully vaccinated per hundred'):
        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        # Add traces
        fig.add_trace(
            go.Scatter(x=sub_df_country['date'], y=sub_df_country['people_vaccinated_per_hundred'], name="people_vaccinated_per_hundred"),
            secondary_y=False,
        )
        
        fig.add_trace(
            go.Scatter(x=sub_df_country['date'], y=sub_df_country['people_fully_vaccinated_per_hundred'], name="people_fully_vaccinated_per_hundred"),
            secondary_y=True,
        )

        # Add figure title
        fig.update_layout(
            title_text="People vaccinated per hundred & People fully vaccinated per hundred of " +country
        )
        # Set y-axes titles
        fig.update_yaxes(title_text="people_vaccinated_per_hundred", secondary_y=False)
        fig.update_yaxes(title_text="people_fully_vaccinated_per_hundred", secondary_y=True)
        
        st.plotly_chart(fig, use_container_width=True)        
        
# Vacinnations progress (countrywise comparison)     
if st.sidebar.checkbox('Vacinnations progress (comparison)'):
    # selection of country from 'location'
    country = st.multiselect("Select the countries: ", sub_df['location'].unique())
    sub_df_country_comparison = sub_df[sub_df['location'].isin(country)].sort_values(by='date', ascending=False).drop(["people_vaccinated","people_fully_vaccinated"], axis = 1)
    sub_df_country_comparison
    
    # data downloading as 'csv'
    @st.cache
    def convert_df(sub_df_country_comparison):
        return sub_df_country_comparison.to_csv().encode('utf-8')
    
    csv = convert_df(sub_df_country_comparison)
    
    st.download_button(
   "Press to download data",
   csv,
   "file.csv",
   "text/csv",
   key='download4-csv'
    )
    
    if st.checkbox('Show/Hide graph of people vaccinated per hundred for countrywise comparison'):
        fig = px.line(sub_df_country_comparison, x='date', y='people_vaccinated_per_hundred', color="location", hover_name="location",title="People vaccinated per hundred")
        st.plotly_chart(fig, use_container_width=True)
        
    if st.checkbox('Show/Hide graph of people fully vaccinated per hundred for countrywise comparison'):
        fig = px.line(sub_df_country_comparison, x='date', y='people_fully_vaccinated_per_hundred', color="location", hover_name="location",title="People fully vaccinated per hundred")
        st.plotly_chart(fig, use_container_width=True)
        
st.sidebar.write("For vaccination dataset (updated each morning, London time), check out the [citation](https://www.nature.com/articles/s41562-021-01122-8)", unsafe_allow_html=True)
    
st.sidebar.write("For source code, check out my [github](https://github.com/vinthegreat84/covitrace1.5)", unsafe_allow_html=True)

st.sidebar.write("If you want to get in touch, you can find me on [linkedin](https://www.linkedin.com/in/vinay-babu-81791015/)", unsafe_allow_html=True)