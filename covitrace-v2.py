import streamlit as st
st.set_page_config(layout="wide", page_title='covitrace - 1.5')

import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly import tools
import io

@st.cache
def fetch_covid():
    url = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv'
#     df = pd.read_csv(url)
    col_list =["location","date","total_cases_per_million", "new_cases_per_million", "new_cases_smoothed_per_million", "total_deaths_per_million", "new_deaths_per_million", "new_deaths_smoothed_per_million"]
    df = pd.read_csv(url, usecols=col_list)
    df['date'] = pd.to_datetime(df['date']).dt.date
    return df
    
df0 = fetch_covid()

@st.cache
def fetch_vaccination():
    url = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv'
    col_list =["location","date","people_vaccinated", "people_vaccinated_per_hundred", "people_fully_vaccinated", "people_fully_vaccinated_per_hundred"]
    df = pd.read_csv(url, usecols=col_list)
    df['date'] = pd.to_datetime(df['date']).dt.date
    return df
    
df = fetch_vaccination()

def plot_html(plot):
    buffer = io.StringIO()
    plot.write_html(buffer, include_plotlyjs='cdn')
    html_bytes = buffer.getvalue().encode()

    st.download_button(
    label='Download HTML',
    data=html_bytes,
    file_name='plot.html',
    mime='text/html'
            )

today = date.today().strftime("%d %b, %Y")

st.title("covitrace - 1.5")
st.write('## Welcome to the Covid Vaccination Analysis')
st.caption('Check the sidebar options (top-left arrow to be clicked, if sidebar is not visible)')
st.write('### Created by Vinay Babu')
st.write('''The covitrace is a tool designed using Python and Streamlit to analyse covid vacinnation.''')

st.sidebar.title("Covid Vaccination Analysis") 

if st.sidebar.checkbox('Covid-19 data as on '+today):
    st.write('#### Covid-19 data as on '+today)    
    df0
    
    with st.expander("Click here for locations with new cases and new deaths as on "+today):
        # top 10 entries of 'new_cases_per_million'
        new_cases_per_million=df0.sort_values('new_cases_per_million', ascending=False).drop_duplicates(['location']).drop(["total_cases_per_million", "new_cases_smoothed_per_million", "total_deaths_per_million", "new_deaths_per_million", "new_deaths_smoothed_per_million"], axis = 1)

        if st.checkbox('Top 10 locations based on new cases per million'):
            st.write('#### Top 10 locations based on new cases per million')            
            st.write(new_cases_per_million.head(10))
            @st.cache
            def convert_df(new_cases_per_million):
                return new_cases_per_million.to_csv(index=False).encode('utf-8')

            new_cases_per_million = convert_df(new_cases_per_million)
            st.download_button("Press to download", new_cases_per_million, "new_cases_per_million.csv", "csv", key='download-new_cases_per_million')            
        
        # top 10 entries of 'new_deaths_per_million'
        new_deaths_per_million=df0.sort_values('new_deaths_per_million', ascending=False).drop_duplicates(['location']).drop(["total_cases_per_million","new_cases_per_million", "new_cases_smoothed_per_million", "total_deaths_per_million", "new_deaths_smoothed_per_million"], axis = 1)

        if st.checkbox('Top 10 locations based on new deaths per million'):
            st.write(new_deaths_per_million.head(10))
            @st.cache
            def convert_df(new_deaths_per_million):
                return new_deaths_per_million.to_csv(index=False).encode('utf-8')

            new_deaths_per_million = convert_df(new_deaths_per_million)
            st.download_button("Press to download", new_deaths_per_million, "new_deaths_per_million.csv", "csv", key='download-new_deaths_per_million')            
        
    # Covid hit (countrywise comparison)     
    if st.checkbox('Covid hit (comparison)'):
        if st.checkbox('Date filter (default is 7 days)'):
            N = 7 # set for '7' days; may be changed for the default view
            start = datetime.now() - timedelta(days=N)
            end = datetime.now()
            
            start_date = st.date_input('Start date', start)
            end_date = st.date_input('End date (default set for today)', end)
            if start_date < end_date:
                pass
                mask = (df0['date'] >= start_date) & (df0['date'] <= end_date)
                df0 = df0.loc[mask]
            else:
                st.error('Error: End date should be chosen after the start day.')

        # selection of country from 'location'
        country = st.multiselect("Select the country: ", df0['location'].unique())
        df0 = df0[df0['location'].isin(country)].sort_values(by='date', ascending=False)
        df0             
            
        # data downloading as 'csv'
        @st.cache
        def convert_df(df0):
            return df.to_csv().encode('utf-8')

        csv = convert_df(df0)

        st.download_button(
       "Press to download data",
       csv,
       "file.csv",
       "text/csv",
       key='download0-csv'
        )
    

        if st.checkbox('Show/Hide graphs of covid hit severity'):
            fig = px.line(df0 , x='date', y='total_cases_per_million', color="location", hover_name="location",title="total cases per million")
            st.plotly_chart(fig, use_container_width=True)
            # exporting the plot to the local machine
            with st.expander("Click to export"):
                plot_html(fig)            

            fig = px.line(df0, x='date', y='new_cases_per_million', color="location", hover_name="location",title="new cases per million")
            st.plotly_chart(fig, use_container_width=True)
            # exporting the plot to the local machine
            with st.expander("Click to export"):
                plot_html(fig)             

            fig = px.line(df0, x='date', y='new_cases_smoothed_per_million', color="location", hover_name="location",title="new cases smoothed per million")
            st.plotly_chart(fig, use_container_width=True)
            # exporting the plot to the local machine
            with st.expander("Click to export"):
                plot_html(fig)             

            fig = px.line(df0, x='date', y='total_deaths_per_million', color="location", hover_name="location",title="total deaths per million")
            st.plotly_chart(fig, use_container_width=True)
            # exporting the plot to the local machine
            with st.expander("Click to export"):
                plot_html(fig)            

            fig = px.line(df0, x='date', y='new_deaths_per_million', color="location", hover_name="location",title="new deaths per million")
            st.plotly_chart(fig, use_container_width=True)
            # exporting the plot to the local machine
            with st.expander("Click to export"):
                plot_html(fig)            

            fig = px.line(df0, x='date', y='new_deaths_smoothed_per_million', color="location", hover_name="location",title="new deaths smoothed per million")
            st.plotly_chart(fig, use_container_width=True)
            # exporting the plot to the local machine
            with st.expander("Click to export"):
                plot_html(fig)            

if st.sidebar.checkbox('Vacinnation data as on '+today):
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

if st.sidebar.checkbox('Date filter (default is 30 days)'):
    N_DAYS = 30 # set for '30' days; may be changed for the default view
    start = datetime.now() - timedelta(days=N_DAYS)
    end = datetime.now()
    
    start_date = st.sidebar.date_input('Start date', start)
    end_date = st.sidebar.date_input('End date (default: today)', end) 
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
        # exporting the plot to the local machine
        with st.expander("Click to export"):
            plot_html(fig)      
        
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
        # exporting the plot to the local machine
        with st.expander("Click to export"):
            plot_html(fig)        
        
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
        # exporting the plot to the local machine
        with st.expander("Click to export"):
            plot_html(fig)        
        
    if st.checkbox('Show/Hide graph of people fully vaccinated per hundred for countrywise comparison'):
        fig = px.line(sub_df_country_comparison, x='date', y='people_fully_vaccinated_per_hundred', color="location", hover_name="location",title="People fully vaccinated per hundred")
        st.plotly_chart(fig, use_container_width=True)
        # exporting the plot to the local machine
        with st.expander("Click to export"):
            plot_html(fig)        
        
st.sidebar.write("For vaccination dataset (updated each morning, London time), check out the [citation](https://www.nature.com/articles/s41562-021-01122-8)", unsafe_allow_html=True)
    
st.sidebar.write("For source code, check out my [github](https://github.com/vinthegreat84/covitrace1.5)", unsafe_allow_html=True)

st.sidebar.write("If you want to get in touch, you can find me on [linkedin](https://www.linkedin.com/in/vinay-babu-81791015/)", unsafe_allow_html=True)