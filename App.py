import streamlit as st
import json
import pandas as pd
import matplotlib.pyplot as plt
from jsonbin import load_key, save_key
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

# -------- load secrets for jsonbin.io --------
jsonbin_secrets = st.secrets["jsonbin"]
api_key = jsonbin_secrets["api_key"]
bin_id = jsonbin_secrets["bin_id"]

# -------- user login --------
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
)

fullname, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status == True:   # login successful
    authenticator.logout('Logout', 'main')   # show logout button
elif authentication_status == False:
    st.error('Username/password is incorrect')
    st.stop()
elif authentication_status == None:
    st.warning('Please enter your username and password')
    st.stop()

#st.write(username)

data = load_key(api_key, bin_id, username)
#st.write(data)



# Funktion um die Daten zu laden
def load_data(filename):
    with open(filename, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data

# Funktion um Daten zu speichern
def save_data(data, filename):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

#save_key(api_key, bin_id, data)

# Daten laden oder leeres Dictionary aufmachen
filename = "data.json"
data = load_data(filename)
if not data:
    data = {}

# Streamlit app und Titel
st.title(":red[Mein Blutdruck-Tagebuch]")

st.subheader("Messwerteingaben")


# Dropdown für das Datum
date = st.date_input("Datum", value=pd.Timestamp.now().date())

# Dropdown für die Zeit
time = st.time_input("Uhrzeit", value=pd.Timestamp.now().time())

# Sliders für Systole, Diastole, und Puls
systole = st.slider("Systole (mmHg)", 0, 200)
diastole = st.slider("Diastole (mmHg)", 0, 200)
pulse = st.slider("Puls (bpm)", 0, 200)

# Submit button 
if st.button("Speichern"):
    # Überprüfen ob Daten für gleiches Datum & Zeit existieren
    if f"{date} {time}" in data:
        st.error("Es wurden bereits Daten für das ausgewählte Datum und die ausgewählte Uhrzeit eingegeben!")
    else:
        # Gemessene Daten im Dictionary speichern
        data[f"{date} {time}"] = {
            "Systole": systole,
            "Diastole": diastole,
            "Puls": pulse
        }
        # Daten speichern im File
        save_data(data, filename)

# Gemessene Daten als Dataframe anzeigen
df = pd.DataFrame(data).T
st.subheader("Gemessene Daten")
st.dataframe(df)

# Liniendiagramm für Diastole, Systole, und Puls
if not df.empty:
    df.index = pd.to_datetime(df.index)
    fig, ax = plt.subplots()
    ax.plot(df.index, df["Systole"], label="Systole")
    ax.plot(df.index, df["Diastole"], label="Diastole")
    ax.plot(df.index, df["Puls"], label="Puls")
    ax.set_xlabel("Datum und Uhrzeit")
    ax.set_ylabel("mmHg / bpm")
    ax.set_title("Blutdruckverlauf")
    ax.legend()
    # Die x-Achse um 45 Grad drehen
    plt.xticks(rotation=45)
    st.subheader("Blutdruckverlauf")
    st.pyplot(fig)

#Informationsfeld zur Messung
st.info('Bevor Sie ihre Messung durchführen, sollten Sie sich in Ruhe 5 Minuten hinsetzten', icon="ℹ️")

#Bild einfügen
from PIL import Image
image= Image.open ("Blutdruck.jpg")
st.image(image,caption="richtiges Blutdruckmessen")
