import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()

# Liste des URL à surveiller
URLS = [
    'https://www.hermes.com/fr/fr/category/femme/sacs-et-petite-maroquinerie/sacs-et-pochettes/#|',
    'https://www.hermes.com/be/fr/category/femme/sacs-et-petite-maroquinerie/sacs-et-pochettes/#|'
]

# Stocker les articles existants pour chaque URL
existing_items = {url: [] for url in URLS}


def check_new_items():
    new_items = []
    for url in URLS:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Adapter cette ligne en fonction de la structure HTML du site
        items = soup.find_all('div', class_='product-item')

        for item in items:
            item_name = item.find('h2').text  # Adapter en fonction de la structure HTML
            if item_name not in existing_items[url]:
                new_items.append((url, item_name))
                existing_items[url].append(item_name)
    
    return new_items

def send_email_alert(new_items):
    sender = os.getenv('EMAIL_SENDER')
    receiver = os.getenv('EMAIL_RECEIVER')
    password = os.getenv('EMAIL_PASSWORD')
    subject = 'Nouveaux articles disponibles!'
    body = "Nouveaux articles trouvés:\n" + "\n".join([f"{item[1]} (URL: {item[0]})" for item in new_items])
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = receiver

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())

def display_current_items():
    current_items = []
    for url in URLS:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Adapter cette ligne en fonction de la structure HTML du site
        items = soup.find_all('div', class_='product-item')

        for item in items:
            item_name = item.find('h2').text  # Adapter en fonction de la structure HTML
            current_items.append((url, item_name))
    
    return current_items

st.title('Surveillance des Nouveaux Articles')

if st.button('Vérifier les articles actuels'):
    current_items = display_current_items()
    if current_items:
        st.write('Articles actuellement détectés:')
        for item in current_items:
            st.write(f"{item[1]} (URL: {item[0]})")
    else:
        st.write("Aucun article détecté.")

if st.button('Lancer la Surveillance'):
    st.write('Surveillance en cours...')
    while True:
        new_items = check_new_items()
        if new_items:
            st.write(f"Nouveaux articles trouvés: {', '.join([item[1] for item in new_items])}")
            send_email_alert(new_items)
        time.sleep(60)  # Vérifier toutes les 60 secondes
