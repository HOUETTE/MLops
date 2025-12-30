"""Interface Streamlit pour tester l'API de détection de spam.

Cette interface permet de :
- Tester la détection de spam sur un message unique
- Tester plusieurs messages en batch
- Voir les métriques du modèle
"""

import streamlit as st
import requests
import json
from typing import Dict, List

# Configuration de la page
st.set_page_config(
    page_title="Spam Detector - G3-MG04",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# URL de l'API (par défaut localhost, modifiable dans la sidebar)
DEFAULT_API_URL = "http://54.75.77.83:8000"

# Sidebar - Configuration
st.sidebar.title("⚙️ Configuration")
api_url = st.sidebar.text_input(
    "URL de l'API",
    value=DEFAULT_API_URL,
    help="URL de l'API FastAPI (ex: http://localhost:8000 ou https://xxx.awsapprunner.com)"
)

# Test de connexion à l'API
st.sidebar.markdown("---")
st.sidebar.subheader("🔌 État de la connexion")

try:
    response = requests.get(f"{api_url}/health", timeout=5)
    if response.status_code == 200:
        health_data = response.json()
        st.sidebar.success("✅ API connectée")
        st.sidebar.json(health_data)
    else:
        st.sidebar.error(f"❌ Erreur : {response.status_code}")
except Exception as e:
    st.sidebar.error(f"❌ API non disponible")
    st.sidebar.caption(str(e))

# Header principal
st.title("📧 Spam Detector API - Groupe G3-MG04")
st.markdown("**Détection de spam avec Machine Learning** | LinearSVC + TF-IDF")
st.markdown("---")

# Onglets
tab1, tab2, tab3 = st.tabs(["🔍 Test Unique", "📊 Test Batch", "📈 Métriques"])

# ========================================
# TAB 1 : Test d'un message unique
# ========================================
with tab1:
    st.header("🔍 Tester un message")

    col1, col2 = st.columns([2, 1])

    with col1:
        # Zone de texte pour le message
        message = st.text_area(
            "Entrez votre message :",
            height=150,
            placeholder="Exemple : WIN FREE MONEY NOW! Click here to claim your prize..."
        )

        # Exemples pré-remplis
        st.caption("💡 Exemples rapides :")
        col_ex1, col_ex2, col_ex3 = st.columns(3)

        with col_ex1:
            if st.button("📧 Email légitime"):
                message = "Meeting scheduled for tomorrow at 3pm in conference room B. Please bring your laptop."
                st.rerun()

        with col_ex2:
            if st.button("🚨 Spam évident"):
                message = "CONGRATULATIONS!!! You won $1,000,000! Click here NOW to claim your prize! Limited time offer!"
                st.rerun()

        with col_ex3:
            if st.button("💰 Offre commerciale"):
                message = "Special discount: Get 50% off on all products this weekend. Visit our store!"
                st.rerun()

        # Bouton de prédiction
        if st.button("🚀 Analyser", type="primary", use_container_width=True):
            if not message:
                st.warning("⚠️ Veuillez entrer un message à analyser")
            else:
                with st.spinner("Analyse en cours..."):
                    try:
                        response = requests.post(
                            f"{api_url}/predict",
                            json={"message": message},
                            timeout=10
                        )

                        if response.status_code == 200:
                            result = response.json()

                            # Affichage du résultat
                            is_spam = result.get("is_spam", False)
                            prediction = result.get("prediction", "unknown")
                            confidence = result.get("confidence", 0)

                            if is_spam:
                                st.error("### 🚨 SPAM DÉTECTÉ")
                                st.markdown(f"**Prédiction :** `{prediction.upper()}`")
                            else:
                                st.success("### ✅ MESSAGE LÉGITIME")
                                st.markdown(f"**Prédiction :** `{prediction.upper()}`")

                            if confidence:
                                st.progress(confidence)
                                st.caption(f"Confiance : {confidence:.2%}")

                            # JSON complet
                            with st.expander("📄 Voir la réponse JSON complète"):
                                st.json(result)
                        else:
                            st.error(f"❌ Erreur {response.status_code}")
                            st.code(response.text)

                    except Exception as e:
                        st.error(f"❌ Erreur de connexion : {str(e)}")

    with col2:
        st.info("""
        ### 📖 Comment ça marche ?

        1. **Entrez un message** dans la zone de texte

        2. **Cliquez sur Analyser** pour obtenir la prédiction

        3. **Résultat :**
           - ✅ **HAM** = Message légitime
           - 🚨 **SPAM** = Message suspect

        4. **Confiance** : Score entre 0 et 1

        ### 🤖 Modèle
        - **Algo :** LinearSVC
        - **Features :** TF-IDF (1-2 grams)
        - **Accuracy :** 99.56%
        """)

# ========================================
# TAB 2 : Test en batch
# ========================================
with tab2:
    st.header("📊 Tester plusieurs messages")

    # Zone de texte pour plusieurs messages
    messages_text = st.text_area(
        "Entrez plusieurs messages (un par ligne) :",
        height=250,
        placeholder="Message 1\nMessage 2\nMessage 3\n..."
    )

    # Bouton exemple
    if st.button("💡 Charger des exemples"):
        messages_text = """Meeting tomorrow at 3pm
WIN FREE MONEY NOW!!!
Can you send me the report?
CONGRATULATIONS! You won a prize!
Project update for next week
Click here to claim your $1000000"""
        st.rerun()

    if st.button("🚀 Analyser tous", type="primary"):
        if not messages_text:
            st.warning("⚠️ Veuillez entrer au moins un message")
        else:
            messages = [m.strip() for m in messages_text.split("\n") if m.strip()]

            if len(messages) > 100:
                st.error("❌ Maximum 100 messages autorisés")
            else:
                with st.spinner(f"Analyse de {len(messages)} message(s)..."):
                    try:
                        response = requests.post(
                            f"{api_url}/predict/batch",
                            json={"messages": messages},
                            timeout=30
                        )

                        if response.status_code == 200:
                            result = response.json()
                            predictions = result.get("predictions", [])

                            # Statistiques
                            col1, col2, col3 = st.columns(3)

                            with col1:
                                st.metric("📨 Total", result.get("total", 0))
                            with col2:
                                st.metric("✅ Ham", result.get("ham_count", 0), delta=None)
                            with col3:
                                st.metric("🚨 Spam", result.get("spam_count", 0), delta=None)

                            st.markdown("---")

                            # Tableau des résultats
                            st.subheader("📋 Résultats détaillés")

                            for i, pred in enumerate(predictions, 1):
                                msg = pred.get("message", "")
                                is_spam = pred.get("is_spam", False)
                                prediction = pred.get("prediction", "")
                                confidence = pred.get("confidence")

                                if is_spam:
                                    st.error(f"**{i}.** 🚨 **SPAM** - {msg[:80]}...")
                                else:
                                    st.success(f"**{i}.** ✅ **HAM** - {msg[:80]}...")

                                if confidence:
                                    st.caption(f"Confiance : {confidence:.2%}")

                            # JSON complet
                            with st.expander("📄 Voir la réponse JSON complète"):
                                st.json(result)
                        else:
                            st.error(f"❌ Erreur {response.status_code}")
                            st.code(response.text)

                    except Exception as e:
                        st.error(f"❌ Erreur : {str(e)}")

# ========================================
# TAB 3 : Métriques du modèle
# ========================================
with tab3:
    st.header("📈 Métriques du Modèle ML")

    if st.button("🔄 Actualiser les métriques"):
        try:
            response = requests.get(f"{api_url}/metrics", timeout=10)

            if response.status_code == 200:
                data = response.json()
                model_metrics = data.get("model_metrics", {})
                system_metrics = data.get("system_metrics", {})

                # Métriques ML
                st.subheader("🤖 Performance du Modèle")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    accuracy = model_metrics.get("accuracy", 0)
                    st.metric("Accuracy", f"{accuracy:.2%}")

                with col2:
                    precision = model_metrics.get("precision", 0)
                    st.metric("Precision", f"{precision:.2%}")

                with col3:
                    recall = model_metrics.get("recall", 0)
                    st.metric("Recall", f"{recall:.2%}")

                with col4:
                    f1 = model_metrics.get("f1", 0)
                    st.metric("F1-Score", f"{f1:.2%}")

                # ROC-AUC
                roc_auc = model_metrics.get("roc_auc", 0)
                st.metric("ROC-AUC", f"{roc_auc:.4f}")

                # Confusion Matrix
                if "confusion_matrix" in model_metrics:
                    st.markdown("---")
                    st.subheader("📊 Matrice de Confusion")
                    cm = model_metrics["confusion_matrix"]

                    col1, col2 = st.columns(2)
                    with col1:
                        st.info(f"**✅ Vrais Négatifs (TN):** {cm[0][0]}")
                        st.warning(f"**⚠️ Faux Positifs (FP):** {cm[0][1]}")
                    with col2:
                        st.warning(f"**⚠️ Faux Négatifs (FN):** {cm[1][0]}")
                        st.success(f"**✅ Vrais Positifs (TP):** {cm[1][1]}")

                # Métriques système
                st.markdown("---")
                st.subheader("⚙️ Métriques Système")

                col1, col2, col3 = st.columns(3)

                with col1:
                    uptime = system_metrics.get("uptime_seconds", 0)
                    hours = uptime // 3600
                    minutes = (uptime % 3600) // 60
                    st.metric("⏱️ Uptime", f"{hours}h {minutes}m")

                with col2:
                    total_predictions = system_metrics.get("total_predictions", 0)
                    st.metric("🔢 Prédictions totales", total_predictions)

                with col3:
                    spam_detected = system_metrics.get("spam_detected", 0)
                    st.metric("🚨 Spam détectés", spam_detected)

                # JSON complet
                with st.expander("📄 Voir toutes les métriques (JSON)"):
                    st.json(data)
            else:
                st.error(f"❌ Erreur {response.status_code}")

        except Exception as e:
            st.error(f"❌ Erreur : {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p><strong>Spam Detector API</strong> - Groupe G3-MG04 | Projet MLOps</p>
    <p>Modèle : LinearSVC + TF-IDF | Accuracy : 99.56%</p>
</div>
""", unsafe_allow_html=True)
