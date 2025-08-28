# Prototype IA sport & santé — version LITE (patchée)

Cette version corrige l'import (`from app.config ...`) en évitant le conflit de nom `app/app.py`.
Le point d'entrée est désormais `app/main.py` et le dossier `app/` est un vrai paquet Python
(grâce à `app/__init__.py`).

## Lancer en local

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app/main.py
```

> Démo pédagogique, pas un dispositif médical. Données non identifiantes uniquement.
