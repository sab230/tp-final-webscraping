import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from function import *

st.set_page_config(
    page_title="Le petit blog ",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

with st.sidebar:
    st.write("Sabrina PAUVADAY")
    st.write("J'ai choisi BeautifulSoup (bs4) pour son interface conviviale, sa capacité à naviguer dans le DOM, sa robustesse face aux erreurs, sa compatibilité avec Python, et son intégration aisée avec d'autres bibliothèques. Ces caractéristiques en font un choix populaire pour le web scraping dans l'application, comme expliqué dans la description avec le lien vers le site scrappé.")
    st.write("https://www.blogdumoderateur.com/")

    # Ajouter un bouton "Historique" dans la barre latérale
    if st.button("Historique"):
        # Charger les données de la base de données pour l'historique
        database = DataBase('journaldugeek')  # Assurez-vous que la connexion à la base de données est rétablie
        queries_df = pd.read_sql_query("SELECT * FROM articles;", database.connection)

        # Afficher la page historique
        st.title("Historique des Requêtes")

        if not queries_df.empty:
            st.dataframe(queries_df)
            st.markdown("## Télécharger l'historique des requêtes au format CSV")
            st.download_button("Télécharger l'historique des requêtes", queries_df.to_csv(index=False), "historique_requetes.csv", "text/csv")
        else:
            st.info("Aucune requête dans l'historique.")

st.title("Le petit blog ")
st.write("Bonjour et bienvenu sur le blog qui permet d'être informé sur les dernières actualités!")

def scrape_page(search, page_number):
    json_data = []
    
    database = DataBase('journaldugeek')
    # Nombre d'articles par page (ajustez en fonction de la pagination réelle du site)
    articles_per_page = 5
    start_index = (page_number - 1) * articles_per_page

    url = f"https://www.blogdumoderateur.com/page/{page_number}/?s={search}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    articles = soup.find_all('article')

    for article in articles[start_index:start_index + articles_per_page]:
        title = article.find('h3').text.replace('\xa0', '')
        image = article.find('img')['src']
        link = article.find('h3').parent['href']
        theme = article.find('span', 'favtag').text
        date = article.find('time').get('datetime').split('T')[0]

        json_data.append({'title': title, 'image': image, 'link': link, 'theme': theme, 'date': date})
        try:
            database.add_row('articles', titre=title, 
            image=image, 
            link=link, theme=theme, author=date)
        except:
            pass

    return json_data

submitted = False

with st.form('Form 1'):
    name = st.text_input('Tapez votre recherche')

    # Demander à l'utilisateur le nombre de pages à afficher
    num_pages = st.slider("Nombre de pages à afficher", min_value=1, max_value=10, value=3)

    if st.form_submit_button('Rechercher'):
        # Afficher le nombre d'articles spécifié sur le nombre de pages spécifié
        scrape_data = []
        for page_number in range(1, num_pages + 1):
            scrape_data.extend(scrape_page(name, page_number))

        df = pd.DataFrame(scrape_data)
        st.write(df)

        # Afficher les images avec une taille spécifiée
        for index, row in df.iterrows():
            st.image(row['image'], caption=row['title'], use_column_width=True, width=200)

        # Enregistrer dans un fichier CSV avec le nom de la requête
        query_filename = f"{name}.csv"
        df.to_csv(query_filename, index=False)

        submitted = True

if submitted:
    st.sidebar.download_button('Télécharger le DataFrame', df.to_csv(), 'data.csv', 'text/csv')
