# Problema de Negócio
A empresa Fome Zero é uma marketplace de restaurantes. Ou seja, seu core business é facilitar o encontro e negociações de clientes e restaurantes. Os restaurantes fazem o cadastro dentro da plataforma da Fome Zero, que disponibiliza informações como endereço, tipo de culinária servida, se possui reservas, se faz entregas e também uma nota de avaliação dos serviços e produtos do restaurante, dentre outras informações.

Um novo CEO foi recém contratado e precisa entender melhor o negócio para conseguir tomar as melhores decisões estratégicas e alavancar ainda mais a Fome Zero, e para isso, ele precisa que seja feita uma análise nos dados da empresa e que sejam gerados dashboards, a partir dessas análises, para responder algumas de suas perguntas

# Metodologia de Solução
A análise dos dados, com as respostas para as perguntas feitas pelo CEO, foi feita em um [Jupyter Notebook](https://github.com/jvictorjordao/fome_zero_project/blob/main/data_exploration.ipynb). Já o [dashboard de visualização](https://fomezero-project.streamlit.app) foi feito em Python, fazendo uso de bibliotecas como pandas, plotly e folium, além do framework Streamlit para deploy do dashboard em cloud. 

Para além do que foi pedido, fez-se ainda uma conversão dos valores monetários contidos no dataset para uma moeda unificada (USD), de maneira com que a comparação entre restaurantes de diferentes partes do mundo (diferentes moedas) ficasse mais justa. Para isso, foi utilizada a biblioteca requests para se obter as taxas de conversão entre as moedas a partir de uma [API](https://www.exchangerate-api.com)
