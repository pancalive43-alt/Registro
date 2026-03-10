import streamlit as st
import pandas as pd
import json
import os
import random
import string
from datetime import datetime

DB_FILE = "database.json"

def carica_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f: return json.load(f)
    return {"classi": [], "studenti": {}, "bacheca": []}

def salva_db(data):
    with open(DB_FILE, "w") as f: json.dump(data, f, indent=4)

st.set_page_config(page_title="ClasseViva - Admin Docente", layout="wide")

# CSS Stile ClasseViva
st.markdown("""
    <style>
    .main { background-color: #f4f7f9; }
    .stTabs [data-baseweb="tab-list"] { background-color: #003366; border-radius: 10px; padding: 5px; }
    .stTabs [data-baseweb="tab"] { color: white; font-weight: bold; }
    .stMetric { background-color: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    h1 { color: #003366; font-family: 'Helvetica Neue', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

db = carica_db()

st.title("👨‍🏫 Registro Docente - ClasseViva PRO")

tabs = st.tabs(["👥 Studenti", "📝 Valutazioni", "📢 Bacheca & Compiti", "📊 Riepilogo"])

with tabs[0]:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Nuova Classe")
        n_cl = st.text_input("Nome Classe (es. 1A)")
        if st.button("Crea Classe"):
            if n_cl and n_cl not in db["classi"]:
                db["classi"].append(n_cl)
                salva_db(db)
                st.success("Classe registrata!")

    with col2:
        st.subheader("Iscrizione Studente")
        nome = st.text_input("Nome e Cognome")
        cl = st.selectbox("Classe", db["classi"])
        if st.button("Genera Credenziali"):
            cod = ''.join(random.choices(string.digits, k=12))
            pw = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            db["studenti"][cod] = {
                "nome": nome, "password": pw, "classe": cl, 
                "voti": [], "assenze": 0, "note": []
            }
            salva_db(db)
            st.code(f"USER: {cod} | PASS: {pw}")

with tabs[1]:
    st.subheader("Inserimento Voti e Note")
    if db["studenti"]:
        cod_s = st.selectbox("Studente", list(db["studenti"].keys()), 
                             format_func=lambda x: f"{db['studenti'][x]['nome']} ({db['studenti'][x]['classe']})")
        
        c1, c2 = st.columns(2)
        with c1:
            voto = st.number_input("Voto", 1.0, 10.0, 6.0, 0.5)
            mat = st.text_input("Materia")
            if st.button("Assegna Voto"):
                db["studenti"][cod_s]["voti"].append({"voto": voto, "materia": mat, "data": datetime.now().strftime("%d/%m")})
                salva_db(db)
                st.success("Voto inserito!")
        with c2:
            nota = st.text_area("Nota Disciplinare")
            if st.button("Invia Nota"):
                db["studenti"][cod_s]["note"].append({"testo": nota, "data": datetime.now().strftime("%d/%m")})
                salva_db(db)
                st.warning("Nota registrata!")
        
        if st.button("Segna Assenza"):
            db["studenti"][cod_s]["assenze"] += 1
            salva_db(db)
            st.info("Assenza conteggiata.")

with tabs[2]:
    st.subheader("Bacheca Scolastica")
    titolo = st.text_input("Titolo Avviso")
    testo = st.text_area("Messaggio/Compiti")
    if st.button("Pubblica"):
        db["bacheca"].append({"titolo": titolo, "testo": testo, "data": datetime.now().strftime("%d/%m %H:%M")})
        salva_db(db)
        st.success("Post pubblicato!")

with tabs[3]:
    st.subheader("Tabellone Scrutinio")
    if db["studenti"]:
        df_data = []
        for k, v in db["studenti"].items():
            media = sum([x['voto'] for x in v['voti']]) / len(v['voti']) if v['voti'] else 0
            df_data.append({"Nome": v['nome'], "Classe": v['classe'], "Media": round(media, 2), "Assenze": v['assenze']})
        st.dataframe(pd.DataFrame(df_data), use_container_width=True)