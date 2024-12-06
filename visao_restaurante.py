#========================================
#Import libraries
#========================================

import pandas as pd
import numpy as np	
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import datetime as dt
from PIL import Image
import re
from haversine import haversine



#========================================
#Import data
#========================================

df = pd.read_csv('train2.csv')

#========================================
#Create a copy of the dataframe
#========================================

df1 = df.copy()


#========================================
#Data cleaning
#========================================

linhas_selecionadas = df1['Delivery_person_Age'] != 'NaN '
df1 = df1.loc[linhas_selecionadas].copy()

linhas_selecionadas = df1['Road_traffic_density'] != 'NaN '
df1 =df1.loc[linhas_selecionadas].copy()

linhas_selecionadas = df1['Festival'] != 'NaN '
df1 = df1.loc[linhas_selecionadas].copy()

linhas_selecionadas = df1['City'] != 'NaN '
df1 = df1.loc[linhas_selecionadas].copy()

linhas_selecionadas = df1['multiple_deliveries'] != 'NaN '
df1 = df1.loc[linhas_selecionadas].copy()

linhas_selecionadas = df1['Delivery_person_Ratings'] != 'NaN '
df1 = df1.loc[linhas_selecionadas].copy()

linhas_selecionadas = df1['Time_taken(min)'] != 'NaN '
df1 = df1.loc[linhas_selecionadas].copy()

#========================================
# Data wrangling
#========================================

df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

df1['Order_Date'] = pd.to_datetime(df1['Order_Date'])

df1['Time_Orderd'] = pd.to_datetime(df1['Time_Orderd'])

df1['Time_Order_picked'] = pd.to_datetime(df1['Time_Order_picked'])

df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

df1['Time_taken_numeric'] = df1['Time_taken(min)'].apply(lambda x: re.findall(r'\d+', str(x))[0])

df1['Time_taken(min)'] =df1['Time_taken(min)'].str.strip(int)

#========================================
# Side Bar
#========================================

st.header('Marketplace - Visão Restaurante')

image_path = 'streamlit.png'
image = Image.open(image_path)
st.sidebar.image(image, width=200)

st.sidebar.markdown('#Curry Company')

st.sidebar.markdown('## Entregas por Cidade')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecionae uma data')

# Filter by date
# filtro de data
date_slider = st.sidebar.slider(
    'Até qual data deseja analisar?',
    value = dt.datetime(2022, 4, 13),
    min_value = dt.datetime(2022, 2, 11), # Data minima do dataframe
    max_value = dt.datetime(2022, 4, 6), # Data maxima do dataframe
	format="DD/MM/YYYY",
)
st.write("Data: " , date_slider)

st.header(date_slider, divider=True)
st.sidebar.markdown("""---""")

# Filter by traffic
# Filtra por transito
traffic_options = st.sidebar.multiselect('Quais as condições do trânsito',
                                         ['Low', 'Medium', 'High', 'Jam'],
                                         default=['Low', 'Medium', 'High', 'Jam',])

st.sidebar.markdown("""---""") 
st.sidebar.markdown('### By José Carlos Carneiro')

# Filtering date
# Filtro por data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# Filtering traffic
# Filtro por transito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

#========================================
# Layout no Streamlit
#========================================

tab1, tab2 = st.tabs(['Visão Gerencial', 'Visão Tática'])

with tab1:
    with st.container():
        st.subheader(''':blue[Métricas Gerais]''')
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            #st.markdown('#### coluna 1')
            entregas_unicas = len(df1.loc[:, 'Delivery_person_ID'].unique())
            st.metric(''' :green[Entregas Unicas]''', entregas_unicas)

        with col2:
            #st.markdown('#### coluna 2')
            col = ['Restaurant_latitude', 'Restaurant_longitude', 
                   'Delivery_location_latitude', 'Delivery_location_longitude']
            df1['Distance'] = df1[col].apply(lambda x: haversine(
                (x['Restaurant_latitude'], x['Restaurant_longitude']),
                (x['Delivery_location_latitude'], x['Delivery_location_longitude'])
                ), axis=1)
            media_distancia = np.round(df1['Distance'].mean(), 2)
            st.metric(''' :green[Distância Media]''', media_distancia)
            
        with col3:
            #st.markdown('#### coluna 3')
            col = ['Time_taken_numeric', 'City']
            media_entrega_cidade = df1.loc[:, col].groupby('City').agg({'Time_taken_numeric': ['mean', 'std']})

            media_entrega_cidade.columns =['Media_tempo', 'Desvio_tempo']

            media_entrega = media_entrega_cidade.reset_index()

        with col4:
            st.markdown('#### coluna 4')
        with col5:
            st.markdown('#### coluna 5')
        with col6:
            st.markdown('#### coluna 6')

    with st.container():
        st.markdown("""---""")
        st.subheader(''':blue[Tempo médio de Entregas por Cidade]''')


    with st.container():
        st.markdown("""---""")
        st.subheader(''':blue[Distribuição do tempo]''')

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('#### coluna1')
        with col2:
            st.markdown('#### coluna 2')
        with col3:
            st.markdown('#### coluna 3')

    with st.container():
        st.markdown("""---""")
        st.subheader(''':blue[Distribuição da distância]''')