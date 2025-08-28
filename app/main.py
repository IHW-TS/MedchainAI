import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import csv, io
from config import MODEL_VERSION, LOG_DIR, APP_NAME
from utils import sha256_of_dict, write_event
from model import FEATURES, predict_proba, global_importance


st.set_page_config(page_title=APP_NAME, page_icon="💡", layout="wide")
st.title("Prototype local IA sport et santé — LITE")
st.caption("Démo pédagogique sans pandas/scikit-learn. Ce logiciel n'est pas un dispositif médical ni un outil clinique.")

mode = st.radio("Mode", ["Bien-être", "Démonstration diagnostique"], index=0)

st.sidebar.subheader("Infos")
st.sidebar.write(f"Version du modèle: {MODEL_VERSION}")
st.sidebar.write("Journaux: app/logs/events.jsonl")

st.header("Entrée des données")
tab1, tab2 = st.tabs(["Saisie manuelle", "Importer un CSV"])

def manual_form():
    with st.form("manual"):
        col1, col2, col3 = st.columns(3)
        with col1:
            age = st.number_input("Âge", min_value=18, max_value=90, value=40)
            bmi = st.number_input("IMC (bmi)", min_value=10.0, max_value=60.0, value=24.0, step=0.1, format="%.1f")
            resting_hr = st.number_input("Fréquence cardiaque au repos", min_value=35, max_value=150, value=65)
        with col2:
            sbp = st.number_input("Pression systolique", min_value=80, max_value=220, value=120)
            exercise = st.number_input("Minutes d'exercice / semaine", min_value=0, max_value=3000, value=180)
            smoker = st.selectbox("Fumeur", ["Non", "Oui"], index=0)
        with col3:
            family = st.selectbox("Antécédents familiaux", ["Non", "Oui"], index=0)
            sex = st.selectbox("Sexe", ["Femme", "Homme"], index=0)
            submitted = st.form_submit_button("Calculer")
    if not submitted:
        return None
    row = {
        "age": float(age),
        "bmi": float(bmi),
        "resting_hr": float(resting_hr),
        "systolic_bp": float(sbp),
        "weekly_minutes_exercise": float(exercise),
        "smoker": 1.0 if smoker == "Oui" else 0.0,
        "family_history": 1.0 if family == "Oui" else 0.0,
        "sex": 1.0 if sex == "Homme" else 0.0,
    }
    return [row]

def csv_upload():
    file = st.file_uploader("CSV avec colonnes: " + ", ".join(FEATURES), type=["csv"])
    if not file:
        st.info("Tu peux partir du sample.csv fourni.")
        return None
    try:
        text = file.read().decode("utf-8")
        rdr = csv.DictReader(io.StringIO(text))
        rows = []
        for r in rdr:
            rows.append({k: float(r[k]) for k in FEATURES})
        return rows
    except Exception as e:
        st.error(f"Erreur lecture CSV: {e}")
        return None

with tab1:
    rows = manual_form()
with tab2:
    rows_csv = csv_upload()
    if rows is None and rows_csv is not None:
        rows = rows_csv

if rows:
    st.header("Résultats")
    results = []
    for r in rows:
        p, contrib = predict_proba(r)
        uncertainty = 1.0 - abs(p - 0.5) * 2.0
        results.append({
            **r,
            "proba_risque": round(float(p), 3),
            "incertitude": round(float(uncertainty), 3)
        })
    st.dataframe(results, use_container_width=True)

    st.subheader("Explications")
    gi = global_importance()
    fig = plt.figure()
    plt.barh([k for k,_ in gi[::-1]], [v for _,v in gi[::-1]])
    plt.xlabel("Poids (absolu)")
    plt.tight_layout()
    st.pyplot(fig)

    r0 = rows[0]
    p0, c0 = predict_proba(r0)
    topk = sorted(c0.items(), key=lambda t: abs(t[1]), reverse=True)[:6]
    fig2 = plt.figure()
    plt.barh([k for k,_ in topk[::-1]], [v for _,v in topk[::-1]])
    plt.xlabel("Contribution locale (approx)")
    plt.tight_layout()
    st.pyplot(fig2)

    st.subheader("Décision humaine")
    colA, colB, colC = st.columns(3)
    validated = colA.button("Valider la recommandation")
    contested = colB.button("Contester et annoter")
    note = colC.text_input("Commentaire")

    payload = {
        "mode": "bien-etre" if mode == "Bien-être" else "demo-diagnostique",
        "model_version": MODEL_VERSION,
        "inputs": r0,
        "input_hash": sha256_of_dict(r0),
        "prediction_proba": float(p0),
        "uncertainty": float(1.0 - abs(p0 - 0.5) * 2.0),
        "user_action": "none",
        "comment": note or ""
    }
    if validated:
        payload["user_action"] = "validated"
    if contested:
        payload["user_action"] = "contested"
    if validated or contested or note:
        write_event(LOG_DIR, payload)
        st.success("Journal mis à jour.")

st.divider()
st.caption("Prototype LITE patché. Aucune finalité clinique.")
