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

# Criando uma cópia do dataframe
#========================================
#Create a copy of the dataframe
#========================================

df1 = df.copy()

# Removendo colunas que contém 'NaN'
#========================================
#Data cleaning
#========================================

col = ['Delivery_person_Age', 'Delivery_person_Ratings', 
       'Order_Date', 'Time_Orderd', 'Time_Order_picked', 
       'multiple_deliveries', 'Festival', 'City', 
       'Road_traffic_density', 'Type_of_order', 'Type_of_vehicle']

for coluna in col:
    linhas_selecionadas = df1[coluna] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :].copy()

# Convertendo as colunas para o tipo correto
#========================================
# Data wrangling
#========================================

df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

df1['Time_Orderd'] = pd.to_datetime(df1['Time_Orderd'])

df1['Time_Order_picked'] = pd.to_datetime(df1['Time_Order_picked'])

df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

# Sparando apenas os valores numericos da coluna Time_taken(min)
df1['Time_taken_numeric'] = df1['Time_taken(min)'].apply(lambda x: re.findall(r'\d+', str(x))[0])

# Convertendo para inteiro
df1['Time_taken_numeric'] = df1['Time_taken_numeric'].astype(int)

#========================================
# Side Bar
#========================================

st.header(''' :blue[Marketplace - Visão Entregadores]''')

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

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        st.title(''' :blue[  Visão Gerencial ]''')

        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            #st.subheader('Maior Idade')
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric(''' :green[Maior Idade]''', maior_idade)

        with col2:
            #st.subheader('Menor Idade')
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric(''':green[Menor Idade]''', menor_idade)

        with col3:
            #st.subheader('Melhor condição')
            melhor_avaliacao = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric(''' :green[Melhor condição]''', melhor_avaliacao)
        with col4:
            #st.subheader('Pior condição')
            pior_avaliacao = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric(''' :green[Pior condição]''', pior_avaliacao)

    with st.container():
        st.markdown("""---""")
        st.subheader(''' :blue[ Avaliação dos Entregadores ]''')

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(''' :green[Avaliação média]''')
            media_por_entregadores = (df1.loc[:, ['Delivery_person_Ratings', 'Delivery_person_ID']]
                                      .groupby('Delivery_person_ID')
                                      .mean()
                                      .reset_index())
            
            #st.markdown(f'{media_por_entregadores.loc[:, "Delivery_person_Ratings"].mean():.2f}')
            st.dataframe(media_por_entregadores)
        
        with col2:
            st.markdown(''' :green[Avaliação mediana]''')
            media_avg_std = (df1.loc[:, ['Delivery_person_Ratings','Road_traffic_density']]
                            .groupby('Road_traffic_density')
                            .agg({'Delivery_person_Ratings': ['mean', 'std']})
                            .reset_index())
            
            st.dataframe(media_avg_std)

            st.markdown(''' :green[Avaliação por tipo de clima]''')
            media_std_weater = (df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']]
                    .groupby('Weatherconditions')
                    .agg({'Delivery_person_Ratings' : ['mean', 'std']})
                    .reset_index())
            st.dataframe(media_std_weater)

    with st.container():
        st.markdown("""---""")
        st.subheader(''' :blue[Tempo de Entrega]''')
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(''' :green[Tempo médio de entrega]''')
            entregador_rapido = (df1[['Delivery_person_ID', 'City', 'Time_taken_numeric']]
                     .groupby(['City', 'Delivery_person_ID'])
                     .max()
                     .reset_index()
                     .sort_values(['City', 'Time_taken_numeric'])
                     .reset_index(drop=True))
            st.dataframe(entregador_rapido.head(10))
            

        with col2:
            st.markdown(''' :green[Tempo mediano de entrega]''')
            entregador_lento = (df1[['Delivery_person_ID', 'City', 'Time_taken_numeric']]
                    .groupby(['City', 'Delivery_person_ID'])
                    .min()
                    .reset_index()
                    .sort_values(['City', 'Time_taken_numeric'])
                    .reset_index(drop=True))
            st.dataframe(entregador_lento.head(10))



