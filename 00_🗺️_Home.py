# IMPORT LIBRARIES
import streamlit as st
from PIL import Image
import pandas as pd
import inflection
import requests
from millify import prettify
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster

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

def create_map(df1):
    map = folium.Map()
    marker_cluster = MarkerCluster().add_to(map)

    for _, line in df1.iterrows():
        folium.Marker(location=[line['latitude'], line['longitude']], 
                      popup = folium.Popup(f"""<h5> <b> {line['restaurant_name']} </b> </h5> <br>
                                                Cozinha: {line['cuisines']} <br>
                                                Preço médio para dois: {line['average_cost_for_two']} ({line['currency']}) <br>
                                                Avaliação: {line['aggregate_rating']} / 5.0 <br> """,
                                                max_width= 500), 
                      icon=folium.Icon(color=line['color_nome'], icon="utensils", prefix='fa')).add_to(marker_cluster)
    
    folium_static(map, width=1024, height=600)

    return None

# =========================
# DATASET
# =========================
df0 = pd.read_csv("dataset\zomato.csv")
df1 = data_clean(df0)

data = get_rates()
df_converted = convert_dataset(df1)



# =========================
# LAYOUT STREAMLIT
# =========================
st.set_page_config(
    page_title='Home',
    page_icon='🗺️',
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

st.sidebar.markdown("""---""")
st.sidebar.markdown("Powered by @victorjoordao")

# BODY
st.markdown('# :red[Projeto Fome Zero]')
st.markdown('## Aqui você encontra os melhores restaurantes ao redor do mundo')
st.markdown("""---""")
st.markdown('### Temos as seguintes métricas dentro da nossa empresa:')

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric('Restaurantes Cadastrados', df1['restaurant_id'].nunique())
col2.metric('Países Cadastrados', df1['country'].nunique())
col3.metric('Cidades Cadastradas', df1['city'].nunique())
col4.metric('Total de avaliações na plataforma', prettify(df1['votes'].sum()).replace(',','.'))
col5.metric('Tipos de culinárias oferecidas', df1['cuisines'].nunique())

create_map(df1)