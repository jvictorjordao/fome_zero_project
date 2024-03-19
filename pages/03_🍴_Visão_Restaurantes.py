# IMPORT LIBRARIES
import streamlit as st
from PIL import Image
import pandas as pd
import inflection
import plotly.express as px
import requests

# =============
# FUNÇÕES
# =============

def data_clean(df1):
    # Linhas Nulas
    df1.dropna(inplace=True)

    # Linhas duplicadas
    df1.drop_duplicates(inplace=True)

    # A coluna "Switch to order menu" possui apenas valores 0
    df1.drop('Switch to order menu', axis=1, inplace=True)

    # Melhorando o nome das colunas
    df1.columns = list(map(lambda x: inflection.titleize(x), df1.columns))
    df1.columns = list(map(lambda x: x.replace(" ", ""), df1.columns))
    df1.columns = list(map(lambda x: inflection.underscore(x), df1.columns))

    # Transformando Country Code
    countries = {
    1: "India",
    14: "Australia",
    30: "Brazil",
    37: "Canada",
    94: "Indonesia",
    148: "New Zeland",
    162: "Philippines",
    166: "Qatar",
    184: "Singapure",
    189: "South Africa",
    191: "Sri Lanka",
    208: "Turkey",
    214: "United Arab Emirates",
    215: "England",
    216: "United States of America",
    }
    df1['country_code'] = df1['country_code'].apply(lambda x: countries[x])
    df1.rename(columns={'country_code':'country'}, inplace=True)

    # Criando a coluna com o nome das cores
    colors = {
    "3F7E00": "darkgreen",
    "5BA829": "green",
    "9ACD32": "lightgreen",
    "CDD614": "orange",
    "FFBA00": "red",
    "CBCBC8": "darkred",
    "FF7800": "darkred",
    }
    df1['color_nome'] = df1['rating_color'].apply(lambda x: colors[x])

    # Categorizando o price range
    price = {1:'cheap',
            2:'normal',
            3:'expensive',
            4:'gourmet'}

    df1['price_range'] = df1['price_range'].apply(lambda x: price[x])

    # Mantendo apenas um tipo de "cuisine"
    df1['cuisines'] = df1['cuisines'].apply(lambda x: x.split(',')[0])

    # Excluindo outlier na coluna average_cost_for_two
    df1.drop(df1[df1['average_cost_for_two']==25000017].index, inplace=True)

    return df1

# Convertendo o average_cost_for_two
# Por otimização, serão criadas duas funções, de maneira que a API seja acessada apenas uma vez
def get_rates(to_currency='USD'):
    '''
        Essa função vai obter a taxa de conversão DE uma determinada moeda PARA todas as outras moedas através de uma API;
        Por padrão, a moeda a ser convertida é o Dolar (USD), mas podemos alterar isso através do parâmetro to_currency
    '''
    url = 'https://api.exchangerate-api.com/v4/latest/'+str(to_currency)
    response = requests.get(url)
    data = response.json()

    return data

def convert_currency(amount, from_currency):
    '''
       Essa função vai realizar a conversão de um determinado valor (amount) a partir de uma determinada moeda (from_currency);
       Como a taxa que obtemos pela API é A PARTIR do dólar, aqui vamos fazer a operação inversa (divisão) para obter a 
       taxa de conversão PARA o dólar.
    '''
    # Salvando a taxa de conversão a partir do json recebido pela API
    exchange_rate = data['rates'][from_currency]
    # Como a coluna original possuía apenas números inteiros, vamos arredondar para manter também números inteiros
    converted_amount = round(amount/exchange_rate)

    return converted_amount

def convert_dataset(df1):
    # Criamos um dicionário para a codificação das moedas de acordo com os códigos aceitos pela API
    currency = {'Botswana Pula(P)':'BWP',
                'Brazilian Real(R$)':'BRL',
                'Dollar($)':'USD',
                'Emirati Diram(AED)':'AED',
                'Indian Rupees(Rs.)':'INR',
                'Indonesian Rupiah(IDR)':'IDR',
                'NewZealand($)':'NZD',
                'Pounds(£)':'GBP',
                'Qatari Rial(QR)':'QAR',
                'Rand(R)':'ZAR',
                'Sri Lankan Rupee(LKR)':'LKR',
                'Turkish Lira(TL)':'TRY'}
    
    df_converted = df1.copy()
    df_converted['average_cost_for_two'] = df1[['currency', 'average_cost_for_two']].apply(lambda x: convert_currency(x['average_cost_for_two'], currency[x['currency']]), axis=1)
    df_converted['currency'] = 'Dollar($)'

    return df_converted

def top_rests(df1):
    dfaux = (df1.sort_values(by=['aggregate_rating', 'restaurant_id'], ascending=[False, True]).head(qtd_top).reset_index(drop=True)
             [['restaurant_name', 'country', 'city', 'cuisines', 'average_cost_for_two', 'aggregate_rating', 'votes']])
    
    return dfaux

def top_cuisines(cuisine):
    df_cuisine = df1[df1['cuisines']==cuisine].sort_values(by=['aggregate_rating', 'restaurant_id'], ascending=[False, True]).head(1)

    return df_cuisine

def plot_rating_per_cuisine(df1, qtd_top):
    avg_rating_per_country = df1[['cuisines', 'aggregate_rating']].groupby('cuisines').mean().sort_values(by='aggregate_rating', ascending=False).reset_index().round(2).head(qtd_top)
    fig = px.bar(avg_rating_per_country, x='cuisines', y='aggregate_rating', 
                text='aggregate_rating', 
                labels={'cuisines':'Culinária', 'aggregate_rating':'Nota média'},
                color='aggregate_rating',
                color_continuous_scale='Reds',
                color_continuous_midpoint=4.3)
    fig.update_layout(yaxis=dict(range=[0, 5]))
    
    return fig

def plot_worst_rating_per_cuisine(df1, qtd_top):
    avg_rating_per_country = df1[['cuisines', 'aggregate_rating']].groupby('cuisines').mean().sort_values(by='aggregate_rating', ascending=True).reset_index().round(2).head(qtd_top)
    fig = px.bar(avg_rating_per_country, x='cuisines', y='aggregate_rating', 
                text='aggregate_rating', 
                labels={'cuisines':'Culinária', 'aggregate_rating':'Nota média'},
                color='aggregate_rating',
                color_continuous_scale='Reds',
                color_continuous_midpoint=4.3)
    fig.update_layout(yaxis=dict(range=[0, 5]))
    
    return fig
# =========================
# DATASET
# =========================
df0 = pd.read_csv("dataset/zomato.csv")
df1 = data_clean(df0)

data = get_rates()
df_converted = convert_dataset(df1)

# =========================
# LAYOUT STREAMLIT
# =========================
st.set_page_config(
    page_title='Visão Restaurantes',
    page_icon='🍴',
    layout='wide'
)

# SIDEBAR
logo = Image.open('logo.png')
col1, col2 = st.sidebar.columns([1,4], gap='small')
col1.image(logo, width=50)
col2.markdown('# Projeto Fome Zero')

st.sidebar.markdown("""---""")
st.sidebar.markdown('## Filtros')

converter = st.sidebar.toggle('Converter valores para Dólar')
if converter:
    st.sidebar.markdown(f"Valores convertidos para dólar segundo cotação do dia {data['date']}")
    df1 = df_converted

filtrar_paises = st.sidebar.toggle('Filtro de Países')
countries = df1['country'].unique().tolist()
if filtrar_paises:
    countries = st.sidebar.multiselect(
        'Escolha os países que deseja visualizar os restaurantes',
        df1['country'].unique().tolist(),
        default=df1['country'].unique().tolist()
    )
df1 = df1[df1['country'].isin(countries)]

qtd_top = st.sidebar.slider('Selecione a quantidade de Restaurantes e Culinárias no Ranking', 1, 20, 10)

selected_cuisines = st.sidebar.multiselect(
    'Visualizar os melhores Restaurantes dos seguintes tipos de culinária:',
    df1['cuisines'].unique().tolist(),
    default=['Italian', 'American', 'Brazilian', 'Japanese', 'Indian'],
    max_selections=5
)

st.sidebar.markdown("""---""")
st.sidebar.markdown("Powered by @victorjoordao")


# BODY
st.markdown('# 🍴 Visão Restaurantes')
with st.container():
    st.markdown(f"<h3 style='text-align: center;'>Top {qtd_top} Restaurantes</h3>", unsafe_allow_html=True)
    st.dataframe(top_rests(df1), use_container_width=True)
st.markdown("""---""")

with st.container():
    st.markdown("<h3 style='text-align: center;'>Melhores Restaurantes por Tipo de Culinária</h3>", unsafe_allow_html=True)
    qtd_cols = len(selected_cuisines)
    cols = st.columns(qtd_cols)

    for i in range(qtd_cols):
        col = cols[i]
        df_cuisine = top_cuisines(selected_cuisines[i])
        col.metric(
            label=f':red[{selected_cuisines[i]}:] {df_cuisine['restaurant_name'].values[0]}',
            value=f'{df_cuisine['aggregate_rating'].values[0]}/5',
            help=f"""
                    País: {df_cuisine['country'].values[0]}\n
                    Cidade: {df_cuisine['city'].values[0]}\n
                    Média do prato para dois: {df_cuisine['average_cost_for_two'].values[0]} {df_cuisine['currency'].values[0]}\n
            """
        )
    
st.markdown('#')

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        fig = plot_rating_per_cuisine(df1, qtd_top)
        st.markdown(f"<h3 style='text-align: center;'>Top {qtd_top} Culinárias com as Melhores Avaliações</h3>", unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = plot_worst_rating_per_cuisine(df1, qtd_top)
        st.markdown(f"<h3 style='text-align: center;'>Top {qtd_top} Culinárias com as Piores Avaliações</h3>", unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)