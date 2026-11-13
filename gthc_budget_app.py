import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import io

# ==============================================================================
# CONFIGURATION & CONSTANTES RaD / HES SO (JOURNÉE TYPE 8H18)
# ==============================================================================
# 8h18 minutes = 8 + 18/60 = 8.30 heures décimales
HOURS_PER_DAY = 8.30
# Nombre moyen de jours ouvrables par mois selon le modèle standard Ra&D
DAYS_PER_MONTH = 21.75
# Capacité théorique mensuelle pour un 100% = 21.75 * 8.30 = 177.915 heures/mois
THEORETICAL_MONTHLY_HOURS_100 = HOURS_PER_DAY * DAYS_PER_MONTH

st.set_page_config(
    page_title="Gestion Budgétaire Ra&D - GTHC HES",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# DONNÉES SYNTHÉTIQUES ANONYMISÉES (MOCK DATA FICTIVES)
# ==============================================================================
@st.cache_data
def get_anonymized_mock_data():
    # 1. Structure Hiérarchique (GTHC & Équipes)
    teams_df = pd.DataFrame([
        {"gthc_id": "GTHC-ICT", "gthc_nom": "Groupe Technologies de l'Information", "team_id": "EQ-01", "team_nom": "Équipe 1 - Data Science & IA"},
        {"gthc_id": "GTHC-ICT", "gthc_nom": "Groupe Technologies de l'Information", "team_id": "EQ-02", "team_nom": "Équipe 2 - IoT & Systèmes Embarqués"},
        {"gthc_id": "GTHC-ICT", "gthc_nom": "Groupe Technologies de l'Information", "team_id": "EQ-03", "team_nom": "Équipe 3 - Ingénierie Logicielle & Sécurité"}
    ])

    # 2. Collaborateurs (Anonymisés)
    collaborators_df = pd.DataFrame([
        {
            "collab_id": "COL-A", "nom_anonyme": "Collaborateur A", "fonction": "Chargé-e de Ra&D HES",
            "taux_activite_pct": 100, "salaire_annuel_charge_chf": 125000.0,
            "heures_enseignement_mois": 30.0, "taux_horaire_std_chf": 80.0
        },
        {
            "collab_id": "COL-B", "nom_anonyme": "Collaborateur B", "fonction": "Collaborateur-trice Ra&D HES",
            "taux_activite_pct": 80, "salaire_annuel_charge_chf": 92000.0,
            "heures_enseignement_mois": 15.0, "taux_horaire_std_chf": 67.30
        },
        {
            "collab_id": "COL-C", "nom_anonyme": "Collaborateur C", "fonction": "Chef-fe de projet Ra&D HES",
            "taux_activite_pct": 100, "salaire_annuel_charge_chf": 148000.0,
            "heures_enseignement_mois": 40.0, "taux_horaire_std_chf": 116.30
        },
        {
            "collab_id": "COL-D", "nom_anonyme": "Collaborateur D", "fonction": "Assistant-e / Doctorant-e",
            "taux_activite_pct": 100, "salaire_annuel_charge_chf": 75000.0,
            "heures_enseignement_mois": 10.0, "taux_horaire_std_chf": 60.00
        },
        {
            "collab_id": "COL-E", "nom_anonyme": "Collaborateur E", "fonction": "Professeur HES",
            "taux_activite_pct": 30, "salaire_annuel_charge_chf": 51000.0,
            "heures_enseignement_mois": 25.0, "taux_horaire_std_chf": 152.15
        }
    ])

    # 3. Multi-affectation aux Équipes (Relation N à N avec pourcentages)
    collab_teams_df = pd.DataFrame([
        {"collab_id": "COL-A", "team_id": "EQ-01", "pct_repartition": 70.0},
        {"collab_id": "COL-A", "team_id": "EQ-03", "pct_repartition": 30.0},
        {"collab_id": "COL-B", "team_id": "EQ-01", "pct_repartition": 100.0},
        {"collab_id": "COL-C", "team_id": "EQ-02", "pct_repartition": 60.0},
        {"collab_id": "COL-C", "team_id": "EQ-03", "pct_repartition": 40.0},
        {"collab_id": "COL-D", "team_id": "EQ-02", "pct_repartition": 100.0},
        {"collab_id": "COL-E", "team_id": "EQ-01", "pct_repartition": 50.0},
        {"collab_id": "COL-E", "team_id": "EQ-02", "pct_repartition": 50.0}
    ])

    # 4. Projets Ra&D (Données fictives)
    projects_df = pd.DataFrame([
        {
            "projet_id": "PROJ-2026-01", "titre": "Projet Alpha (Innosuisse)", "type_financement": "Innosuisse",
            "budget_total_chf": 246232.0, "reserve_chf": 10000.0, "depenses_constatees_chf": 28576.0,
            "date_debut": "2026-01-01", "date_fin": "2028-01-11", "statut": "Actif"
        },
        {
            "projet_id": "PROJ-2026-02", "titre": "Projet Bêta (FNS)", "type_financement": "FNS",
            "budget_total_chf": 180000.0, "reserve_chf": 8000.0, "depenses_constatees_chf": 10000.0,
            "date_debut": "2026-09-01", "date_fin": "2027-12-31", "statut": "Actif"
        },
        {
            "projet_id": "PROJ-2026-03", "titre": "Projet Gamma (Mandat Industrie)", "type_financement": "Mandat Direct",
            "budget_total_chf": 120000.0, "reserve_chf": 0.0, "depenses_constatees_chf": 55000.0,
            "date_debut": "2026-02-01", "date_fin": "2026-12-31", "statut": "Actif"
        }
    ])

    # 5. Affectations Collaborateurs - Projets (Planning RH mensuel prévisionnel)
    allocations_df = pd.DataFrame([
        {"projet_id": "PROJ-2026-01", "collab_id": "COL-A", "heures_mois_prevues": 55.0, "taux_facture_chf": 67.30},
        {"projet_id": "PROJ-2026-01", "collab_id": "COL-B", "heures_mois_prevues": 45.0, "taux_facture_chf": 67.30},
        {"projet_id": "PROJ-2026-01", "collab_id": "COL-E", "heures_mois_prevues": 9.0, "taux_facture_chf": 152.15},
        {"projet_id": "PROJ-2026-02", "collab_id": "COL-C", "heures_mois_prevues": 70.0, "taux_facture_chf": 67.30},
        {"projet_id": "PROJ-2026-02", "collab_id": "COL-D", "heures_mois_prevues": 60.0, "taux_facture_chf": 60.00},
        {"projet_id": "PROJ-2026-03", "collab_id": "COL-A", "heures_mois_prevues": 30.0, "taux_facture_chf": 130.00},
        {"projet_id": "PROJ-2026-03", "collab_id": "COL-C", "heures_mois_prevues": 25.0, "taux_facture_chf": 160.00}
    ])

    return teams_df, collaborators_df, collab_teams_df, projects_df, allocations_df


# Initialisation Session State
if "data_loaded" not in st.session_state:
    t_df, c_df, ct_df, p_df, a_df = get_anonymized_mock_data()
    st.session_state.teams_df = t_df
    st.session_state.collaborators_df = c_df
    st.session_state.collab_teams_df = ct_df
    st.session_state.projects_df = p_df
    st.session_state.allocations_df = a_df
    st.session_state.data_loaded = True

teams_df = st.session_state.teams_df
collaborators_df = st.session_state.collaborators_df
collab_teams_df = st.session_state.collab_teams_df
projects_df = st.session_state.projects_df
allocations_df = st.session_state.allocations_df

# ==============================================================================
# BARRE LATÉRALE - FILTRES & PARAMÈTRES DE SUIVI
# ==============================================================================
st.sidebar.title("🎛️ Pilotage Ra&D GTHC")
st.sidebar.markdown("---")

filter_gthc = st.sidebar.selectbox("Filtrer par Groupe (GTHC) :", options=["Tous"] + list(teams_df["gthc_nom"].unique()))
filter_team = st.sidebar.selectbox("Filtrer par Équipe :", options=["Toutes"] + list(teams_df["team_nom"].unique()))

st.sidebar.markdown("---")
st.sidebar.subheader("📅 Paramètres temporels")
date_suivi = st.sidebar.date_input("Date du suivi (Bascule Réel / Futur) :", value=date(2026, 10, 1))
horizon_fin = st.sidebar.date_input("Fin de projection :", value=date(2028, 12, 31))

st.sidebar.markdown("---")
st.sidebar.caption("⚙️ HES-SO standard: 8h18/jour (8.30h), 21.75j/mois")

# ==============================================================================
# EN-TÊTE PRINCIPAL
# ==============================================================================
st.title("⚖️ Gestion Budgétaire & RH Ra&D (GTHC HES / CHF)")
st.caption("Application de pilotage financier et simulation RH selon la méthodologie institutionnelle Ra&D.")

# ==============================================================================
# ONGLETS DE NAVIGATION
# ==============================================================================
tab_dash, tab_collab, tab_proj, tab_sim, tab_traj, tab_pers = st.tabs([
    "📊 Tableau de Bord GTHC",
    "👥 Collaborateurs & Affectations N-N",
    "📁 Projets & Jours Restants (8h18)",
    "💼 Couverture & Simulation Embauche",
    "📈 Projections Mensuelles (31 Déc)",
    "⚙️ Persistance & Données Excel"
])

# ------------------------------------------------------------------------------
# TAB 1 : TABLEAU DE BORD GTHC
# ------------------------------------------------------------------------------
with tab_dash:
    st.header("📊 Vue d'ensemble synthétique du Portefeuille Ra&D")

    # Calculs métriques globales
    total_b = projects_df["budget_total_chf"].sum()
    total_dep = projects_df["depenses_constatees_chf"].sum()
    total_res = projects_df["reserve_chf"].sum()

    # Budget restant total
    solde_total = total_b - total_dep - total_res

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Budget Total Portefeuille", f"{total_b:,.2f} CHF".replace(",", "'"))
    col2.metric("Réel Constaté (Au suivi)", f"{total_dep:,.2f} CHF".replace(",", "'"))
    col3.metric("Réserves Mises de Côté", f"{total_res:,.2f} CHF".replace(",", "'"))
    col4.metric("Solde Disponible Brut", f"{solde_total:,.2f} CHF".replace(",", "'"), delta="Disponible")

    st.markdown("---")
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Plafond Budgétaire vs Dépenses par Projet (CHF)")
        fig_bar = px.bar(
            projects_df,
            x="titre",
            y=["depenses_constatees_chf", "reserve_chf", "budget_total_chf"],
            barmode="group",
            labels={"value": "CHF", "variable": "Poste", "titre": "Projet"},
            color_discrete_sequence=["#e74c3c", "#f39c12", "#2980b9"]
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        st.subheader("Répartition des Salaires Chargés par Équipe (N-N)")
        # Calcul masse salariale proratisée par équipe
        ct_m = collab_teams_df.merge(collaborators_df, on="collab_id").merge(teams_df, on="team_id")
        ct_m["salarial_equipe_chf"] = ct_m["salaire_annuel_charge_chf"] * (ct_m["pct_repartition"] / 100.0)
        team_sal_df = ct_m.groupby("team_nom")["salarial_equipe_chf"].sum().reset_index()

        fig_pie = px.pie(
            team_sal_df,
            names="team_nom",
            values="salarial_equipe_chf",
            hole=0.4,
            title="Répartition Salariale Annuelle"
        )
        st.plotly_chart(fig_pie, use_container_width=True)

# ------------------------------------------------------------------------------
# TAB 2 : COLLABORATEURS & AFFECTATIONS N-N
# ------------------------------------------------------------------------------
with tab_collab:
    st.header("👥 Multi-affectation aux Équipes (N-N) & Gestion des Capacités")
    st.info("💡 **Capacité théorique HES** : Calculée sur la base de 8h18/jour (8.30h décimales) et 21.75 jours/mois = **177.915 h/mois** pour un 100%. Les heures d'enseignement sont déduites de la capacité disponible sur projets.")

    # Calcul capacité mensuelle disponible
    c_df_calc = collaborators_df.copy()
    c_df_calc["capacite_brute_h"] = (c_df_calc["taux_activite_pct"] / 100.0) * THEORETICAL_MONTHLY_HOURS_100
    c_df_calc["capacite_dispo_proj_h"] = c_df_calc.apply(
        lambda r: max(0.0, r["capacite_brute_h"] - r["heures_enseignement_mois"]), axis=1
    )
    c_df_calc["capacite_dispo_proj_j_8h18"] = c_df_calc["capacite_dispo_proj_h"] / HOURS_PER_DAY

    st.subheader("1. Répertoire des Collaborateurs & Capacité Disponible")
    st.dataframe(
        c_df_calc[[
            "collab_id", "nom_anonyme", "fonction", "taux_activite_pct",
            "salaire_annuel_charge_chf", "heures_enseignement_mois",
            "capacite_brute_h", "capacite_dispo_proj_h", "capacite_dispo_proj_j_8h18"
        ]].style.format({
            "salaire_annuel_charge_chf": "{:,.2f} CHF",
            "heures_enseignement_mois": "{:.1f} h",
            "capacite_brute_h": "{:.1f} h",
            "capacite_dispo_proj_h": "{:.1f} h",
            "capacite_dispo_proj_j_8h18": "{:.1f} j (8h18)"
        }),
        use_container_width=True
    )

    st.subheader("2. Matrice Multi-Équipes (N-to-N) & Ventilations des Coûts")
    ct_full = collab_teams_df.merge(collaborators_df, on="collab_id").merge(teams_df, on="team_id")
    ct_full["part_salaire_equipe_chf"] = ct_full["salaire_annuel_charge_chf"] * (ct_full["pct_repartition"] / 100.0)

    st.dataframe(
        ct_full[[
            "nom_anonyme", "team_nom", "pct_repartition", "salaire_annuel_charge_chf", "part_salaire_equipe_chf"
        ]].style.format({
            "pct_repartition": "{:.0f}%",
            "salaire_annuel_charge_chf": "{:,.2f} CHF",
            "part_salaire_equipe_chf": "{:,.2f} CHF"
        }),
        use_container_width=True
    )

# ------------------------------------------------------------------------------
# TAB 3 : PROJETS & JOURS RESTANTS (8H18)
# ------------------------------------------------------------------------------
with tab_proj:
    st.header("📁 Suivi Budgétaire & Calcul Automatique des Jours Restants (8h18)")

    p_df_calc = projects_df.copy()
    p_df_calc["solde_disponible_chf"] = p_df_calc["budget_total_chf"] - p_df_calc["depenses_constatees_chf"] - p_df_calc["reserve_chf"]

    # Obtenir le taux horaire moyen facturé sur chaque projet
    rates_agg = allocations_df.groupby("projet_id")["taux_facture_chf"].mean().reset_index()
    p_df_calc = p_df_calc.merge(rates_agg, on="projet_id", how="left").fillna({"taux_facture_chf": 80.0})

    p_df_calc["heures_restantes"] = p_df_calc["solde_disponible_chf"] / p_df_calc["taux_facture_chf"]
    p_df_calc["jours_restants_8h18"] = p_df_calc["heures_restantes"] / HOURS_PER_DAY

    st.dataframe(
        p_df_calc[[
            "projet_id", "titre", "type_financement", "budget_total_chf",
            "depenses_constatees_chf", "reserve_chf", "solde_disponible_chf",
            "taux_facture_chf", "heures_restantes", "jours_restants_8h18", "statut"
        ]].style.format({
            "budget_total_chf": "{:,.2f} CHF",
            "depenses_constatees_chf": "{:,.2f} CHF",
            "reserve_chf": "{:,.2f} CHF",
            "solde_disponible_chf": "{:,.2f} CHF",
            "taux_facture_chf": "{:.2f} CHF/h",
            "heures_restantes": "{:,.1f} h",
            "jours_restants_8h18": "{:,.1f} j (8h18)"
        }),
        use_container_width=True
    )

# ------------------------------------------------------------------------------
# TAB 4 : COUVERTURE & SIMULATION EMBAUCHE
# ------------------------------------------------------------------------------
with tab_sim:
    st.header("💼 Couverture Salariale & Module de Simulation d'Embauche")

    col_c, col_s = st.columns([1, 1])

    with col_c:
        st.subheader("1. Couverture des Salaires par les Projets")
        # Chiffre d'affaires annuel facturable par les heures de projets attribuées
        alloc_merged = allocations_df.merge(collaborators_df, on="collab_id")
        alloc_merged["ca_annuel_chf"] = alloc_merged["heures_mois_prevues"] * alloc_merged["taux_facture_chf"] * 12.0
        ca_per_collab = alloc_merged.groupby("nom_anonyme")["ca_annuel_chf"].sum().reset_index()

        cov_df = collaborators_df.merge(ca_per_collab, on="nom_anonyme", how="left").fillna({"ca_annuel_chf": 0.0})
        cov_df["taux_couverture_pct"] = (cov_df["ca_annuel_chf"] / cov_df["salaire_annuel_charge_chf"]) * 100.0
        cov_df["solde_non_couvert_chf"] = cov_df["salaire_annuel_charge_chf"] - cov_df["ca_annuel_chf"]

        st.dataframe(
            cov_df[[
                "nom_anonyme", "salaire_annuel_charge_chf", "ca_annuel_chf", "taux_couverture_pct", "solde_non_couvert_chf"
            ]].style.format({
                "salaire_annuel_charge_chf": "{:,.2f} CHF",
                "ca_annuel_chf": "{:,.2f} CHF",
                "taux_couverture_pct": "{:.1f}%",
                "solde_non_couvert_chf": "{:,.2f} CHF"
            }),
            use_container_width=True
        )

    with col_s:
        st.subheader("2. 🤖 Simulateur d'Embauche (Scénarios RH)")
        st.write("Évaluez si les solde financiers des projets permettent de financer un nouveau recrutement.")

        with st.form("form_embauche"):
            cand_nom = st.text_input("Intitulé du poste / Candidat :", value="Chercheur Post-Doc Ra&D")
            target_proj = st.selectbox("Projet d'affectation :", options=projects_df["titre"].unique())
            cand_taux = st.slider("Taux d'activité (%) :", min_value=10, max_value=100, value=80, step=10)
            cand_salaire = st.number_input("Salaire annuel chargé employeur (CHF) :", value=90000.0, step=2500.0)
            cand_hourly_rate = st.number_input("Taux horaire d'imputation projet (CHF/h) :", value=67.30, step=2.5)
            cand_duree = st.slider("Durée du contrat (mois) :", min_value=1, max_value=24, value=12)

            btn_sim = st.form_submit_button("Lancer la Simulation")

        if btn_sim:
            cout_employeur_periode = (cand_salaire * (cand_taux / 100.0)) * (cand_duree / 12.0)
            proj_data = projects_df[projects_df["titre"] == target_proj].iloc[0]
            solde_dispo_projet = proj_data["budget_total_chf"] - proj_data["depenses_constatees_chf"] - proj_data["reserve_chf"]

            st.markdown(f"**Résultat du test de viabilité pour `{cand_nom}` :**")
            st.write(f"- Coût employeur total sur {cand_duree} mois : **{cout_employeur_periode:,.2f} CHF**")
            st.write(f"- Solde disponible sur le projet `{target_proj}` : **{solde_dispo_projet:,.2f} CHF**")

            taux_couv_sim = (solde_dispo_projet / cout_employeur_periode) * 100.0 if cout_employeur_periode > 0 else 0

            if solde_dispo_projet >= cout_employeur_periode:
                st.success(f"✅ Budget suffisant ! Le projet couvre 100% de l'embauche. (Taux de couverture : {taux_couv_sim:.1f}%)")
            else:
                manquant = cout_employeur_periode - solde_dispo_projet
                st.error(f"⚠️ Déficit de financement ! Montant non couvert : **{manquant:,.2f} CHF** (Taux de couverture : {taux_couv_sim:.1f}%)")

# ------------------------------------------------------------------------------
# TAB 5 : PROJECTIONS MENSUELLES (31 DÉCEMBRE)
# ------------------------------------------------------------------------------
with tab_traj:
    st.header("📈 Projections Mensuelles au 31 Décembre & Horizon Ra&D")

    months_list = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Août", "Sep", "Oct (Suivi)", "Nov", "Déc"]
    # Trajectoires
    reel_cumul = [12000, 25000, 40000, 55000, 72000, 88000, 102000, 115000, 128000, 128000, None, None]
    proj_cumul = [None, None, None, None, None, None, None, None, None, 128000, 155000, 185000]

    fig_traj = go.Figure()
    fig_traj.add_trace(go.Scatter(x=months_list, y=reel_cumul, mode="lines+markers", name="Réel Constaté (CHF)", line=dict(color="#2980b9", width=3)))
    fig_traj.add_trace(go.Scatter(x=months_list, y=proj_cumul, mode="lines+markers", name="Projection RH Futurs (CHF)", line=dict(color="#e67e22", width=3, dash="dash")))
    fig_traj.add_trace(go.Scatter(x=months_list, y=[total_b]*12, mode="lines", name="Budget Total Portefeuille", line=dict(color="#c0392b", width=2, dash="dot")))

    fig_traj.update_layout(
        title="Trajectoire Budgétaire Mensuelle (Réel vs Prévisionnel RH)",
        xaxis_title="Mois",
        yaxis_title="Montant Cumulé (CHF)",
        hovermode="x unified"
    )
    st.plotly_chart(fig_traj, use_container_width=True)

# ------------------------------------------------------------------------------
# TAB 6 : PERSISTANCE & DONNÉES EXCEL
# ------------------------------------------------------------------------------
with tab_pers:
    st.header("⚙️ Migration des Données & Persistance Excel")
    st.markdown("""
    Cette section permet d'exporter l'état actuel sous forme de modèle Excel et de charger vos vrais fichiers institutionnels en toute sécurité.

    **Procédure de transition vers vos vraies données :**
    1. Téléchargez le modèle d'exportation ci-dessous.
    2. Remplacez les lignes anonymisées par vos données réelles (Collaborateurs, Projets, Multi-affectations).
    3. Importez votre fichier Excel réexposé.
    """)

    # Export Excel en mémoire
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        collaborators_df.to_excel(writer, sheet_name="Personnel", index=False)
        teams_df.to_excel(writer, sheet_name="Equipes", index=False)
        collab_teams_df.to_excel(writer, sheet_name="Affectations_Equipes", index=False)
        projects_df.to_excel(writer, sheet_name="Projets", index=False)
        allocations_df.to_excel(writer, sheet_name="Affectations_Projets", index=False)

    st.download_button(
        label="📥 Télécharger la structure de données complète (Excel .xlsx)",
        data=buffer.getvalue(),
        file_name="modele_pilotage_budget_rad.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.markdown("---")
    st.subheader("Charger vos fichiers réels")
    uploaded_file = st.file_uploader("Sélectionner votre fichier Excel (.xlsx)", type=["xlsx"])
    if uploaded_file is not None:
        try:
            xls = pd.ExcelFile(uploaded_file)
            st.success(f"Fichier '{uploaded_file.name}' prêt ! Feuilles détectées : {xls.sheet_names}")
        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier : {e}")
