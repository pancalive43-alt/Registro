import streamlit as st
import json
import os
import pandas as pd

DB_FILE = "database.json"

def carica_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f: return json.load(f)
    return {"studenti": {}, "bacheca": []}

st.set_page_config(page_title="ClasseViva - Portale Studenti", layout="wide")

# CSS Stile ClasseViva Light
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    .voto-card { padding: 10px; border-radius: 5px; border-left: 5px solid #003366; background: #f8f9fa; margin-bottom: 5px; }
    .stSidebar { background-color: #003366; }
    .stSidebar * { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

if 'user' not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:
    st.title("🎓 Accesso Studente")
    c1, c2 = st.columns([1, 1])
    with c1:
        user_in = st.text_input("Codice Utente")
        pass_in = st.text_input("Password", type="password")
        if st.button("Entra"):
            db = carica_db()
            if user_in in db["studenti"] and db["studenti"][user_in]["password"] == pass_in:
                st.session_state.user = user_in
                st.rerun()
            else:
                st.error("Credenziali non valide")
else:
    db = carica_db()
    u = db["studenti"][st.session_state.user]
    
    st.title(f"Benvenuto, {u['nome']}")
    st.caption(f"Classe {u['classe']} | Registro Elettronico")

    t1, t2, t3 = st.tabs(["📈 Andamento", "📝 Note & Assenze", "📢 Bacheca"])

    with t1:
        voti_num = [x['voto'] for x in u['voti']]
        media = sum(voti_num) / len(voti_num) if voti_num else 0
        
        c1, c2 = st.columns(2)
        c1.metric("Media Generale", f"{media:.2f}", delta=round(media-6, 2) if media else 0)
        c2.metric("Assenze Totali", f"{u['assenze']} gg")
        
        st.subheader("Ultimi Voti")
        for v in reversed(u['voti']):
            st.markdown(f"""<div class='voto-card'><b>{v['materia']}</b>: {v['voto']} <br><small>Data: {v['data']}</small></div>""", unsafe_allow_html=True)

    with t2:
        st.subheader("Note Disciplinari")
        if u['note']:
            for n in u['note']:
                st.error(f"Data: {n['data']} - {n['testo']}")
        else:
            st.success("Nessuna nota disciplinare presente.")

    with t3:
        st.subheader("Comunicazioni della Scuola")
        for b in reversed(db["bacheca"]):
            with st.expander(f"{b['data']} - {b['titolo']}"):
                st.write(b['testo'])

    if st.sidebar.button("Esci"):
        st.session_state.user = None
        st.rerun()