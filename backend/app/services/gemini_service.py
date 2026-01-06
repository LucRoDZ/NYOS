import google.generativeai as genai
from app.config import GOOGLE_API_KEY
from sqlalchemy.orm import Session
from app import models
from datetime import datetime, timedelta
import json

genai.configure(api_key=GOOGLE_API_KEY)


def get_data_context(db: Session) -> str:
    batches = (
        db.query(models.Batch)
        .order_by(models.Batch.manufacturing_date.desc())
        .limit(100)
        .all()
    )
    qc_results = (
        db.query(models.QCResult)
        .order_by(models.QCResult.test_date.desc())
        .limit(100)
        .all()
    )
    complaints = db.query(models.Complaint).all()
    capas = db.query(models.CAPA).all()

    context = f"""
Données de l'usine pharmaceutique - Paracetamol 500mg:

LOTS RÉCENTS ({len(batches)} lots):
"""
    for b in batches[:20]:
        context += f"- {b.batch_id}: {b.manufacturing_date.strftime('%Y-%m-%d') if b.manufacturing_date else 'N/A'}, Machine: {b.machine}, Dureté: {b.hardness}N, Rendement: {b.yield_percent}%\n"

    if qc_results:
        context += f"\nRÉSULTATS QC ({len(qc_results)} tests):\n"
        for qc in qc_results[:20]:
            context += f"- Lot {qc.batch_id}: Dissolution: {qc.dissolution}%, Essai: {qc.assay}%, Résultat: {qc.result}\n"

    if complaints:
        context += f"\nPLAINTES ({len(complaints)} total, {len([c for c in complaints if c.status == 'open'])} ouvertes):\n"
        for c in complaints[:10]:
            context += f"- {c.complaint_id}: {c.category} - {c.severity} - {c.description[:50]}...\n"

    if capas:
        context += f"\nCAPAs ({len(capas)} total, {len([c for c in capas if c.status == 'open'])} ouvertes):\n"
        for capa in capas[:10]:
            context += f"- {capa.capa_id}: {capa.type} - {capa.description[:50]}...\n"

    return context


SYSTEM_PROMPT = """Tu es NYOS, un assistant IA expert en qualité pharmaceutique et analyse APR (Annual Product Review).
Tu analyses les données de production de comprimés de Paracetamol 500mg.

Ton rôle:
1. Détecter les tendances et dérives dans les données
2. Identifier les anomalies et signaux faibles
3. Résumer clairement la situation qualité
4. Recommander des actions si nécessaire

Règles:
- Sois concis et précis
- Utilise des données chiffrées quand possible
- Signale tout problème potentiel
- Réponds en français
- Formate tes réponses avec des bullet points si nécessaire
"""


async def chat_with_gemini(message: str, db: Session) -> str:
    try:
        context = get_data_context(db)
        model = genai.GenerativeModel("gemini-3.5-flash")

        full_prompt = f"""{SYSTEM_PROMPT}

CONTEXTE DES DONNÉES:
{context}

QUESTION DE L'UTILISATEUR:
{message}

RÉPONSE:"""

        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Erreur de connexion à Gemini: {str(e)}. Vérifiez votre clé API."


async def analyze_trends(db: Session, parameter: str = "hardness", days: int = 30):
    batches = db.query(models.Batch).order_by(models.Batch.manufacturing_date).all()

    if not batches:
        return {"error": "Pas assez de données", "dates": [], "values": []}

    max_date = max(b.manufacturing_date for b in batches if b.manufacturing_date)
    cutoff = max_date - timedelta(days=days)

    filtered = [
        b for b in batches if b.manufacturing_date and b.manufacturing_date >= cutoff
    ]

    if len(filtered) < 2:
        return {
            "error": "Pas assez de données pour cette période",
            "dates": [],
            "values": [],
        }

    values = [
        getattr(b, parameter, 0)
        for b in filtered
        if getattr(b, parameter, None) is not None
    ]
    dates = [
        b.manufacturing_date.strftime("%Y-%m-%d")
        for b in filtered
        if getattr(b, parameter, None) is not None
    ]

    if len(values) < 2:
        return {"error": "Pas assez de données", "dates": [], "values": []}

    trend = "stable"
    alert = False
    if len(values) >= 5:
        mid = len(values) // 2
        first_avg = sum(values[:mid]) / mid
        last_avg = sum(values[mid:]) / (len(values) - mid)
        change = ((last_avg - first_avg) / first_avg) * 100 if first_avg else 0

        if change > 5:
            trend = "hausse"
            alert = True
        elif change < -5:
            trend = "baisse"
            alert = True

    return {
        "dates": dates,
        "values": values,
        "parameter": parameter,
        "trend_direction": trend,
        "alert": alert,
        "average": round(sum(values) / len(values), 2) if values else 0,
        "min": round(min(values), 2) if values else 0,
        "max": round(max(values), 2) if values else 0,
        "count": len(values),
    }


def get_full_stats(db: Session) -> dict:
    from sqlalchemy import func

    batches = db.query(models.Batch).all()
    qc_results = db.query(models.QCResult).all()
    complaints = db.query(models.Complaint).all()
    capas = db.query(models.CAPA).all()
    equipment = db.query(models.Equipment).all()

    stats = {
        "total_batches": len(batches),
        "avg_hardness": (
            round(sum(b.hardness for b in batches if b.hardness) / len(batches), 2)
            if batches
            else 0
        ),
        "avg_yield": (
            round(
                sum(b.yield_percent for b in batches if b.yield_percent) / len(batches),
                2,
            )
            if batches
            else 0
        ),
        "machines": {},
        "qc_pass_rate": (
            round(
                len([q for q in qc_results if q.result == "pass"])
                / len(qc_results)
                * 100,
                1,
            )
            if qc_results
            else 0
        ),
        "complaints_by_category": {},
        "complaints_open": len([c for c in complaints if c.status == "open"]),
        "capas_open": len([c for c in capas if c.status == "open"]),
        "equipment_due": len([e for e in equipment if e.status == "due"]),
    }

    for b in batches:
        if b.machine not in stats["machines"]:
            stats["machines"][b.machine] = {
                "count": 0,
                "hardness_sum": 0,
                "yield_sum": 0,
            }
        stats["machines"][b.machine]["count"] += 1
        stats["machines"][b.machine]["hardness_sum"] += b.hardness or 0
        stats["machines"][b.machine]["yield_sum"] += b.yield_percent or 0

    for m, data in stats["machines"].items():
        if data["count"] > 0:
            data["avg_hardness"] = round(data["hardness_sum"] / data["count"], 2)
            data["avg_yield"] = round(data["yield_sum"] / data["count"], 2)

    for c in complaints:
        cat = c.category or "Unknown"
        stats["complaints_by_category"][cat] = (
            stats["complaints_by_category"].get(cat, 0) + 1
        )

    return stats


async def generate_summary_stream(db: Session):
    try:
        context = get_data_context(db)
        stats = get_full_stats(db)
        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = f"""{SYSTEM_PROMPT}

CONTEXTE DES DONNÉES:
{context}

STATISTIQUES:
- Total lots: {stats['total_batches']}
- Dureté moyenne: {stats['avg_hardness']}N
- Rendement moyen: {stats['avg_yield']}%
- Taux de conformité QC: {stats['qc_pass_rate']}%
- Plaintes ouvertes: {stats['complaints_open']}
- CAPAs ouvertes: {stats['capas_open']}
- Équipements à calibrer: {stats['equipment_due']}
- Plaintes par catégorie: {stats['complaints_by_category']}
- Performance par machine: {stats['machines']}

Génère un résumé exécutif détaillé de l'état de l'usine.
Structure ta réponse avec:
1. **État Général** - (🟢 Bon / 🟡 Attention / 🔴 Critique)
2. **Performance Production** - rendement, volumes
3. **Qualité** - résultats QC, tendances
4. **Problèmes Détectés** - plaintes, CAPAs, anomalies
5. **Recommandations** - actions prioritaires

Utilise des bullet points et du texte en **gras** pour les points importants.

RÉSUMÉ:"""

        response = model.generate_content(prompt, stream=True)
        for chunk in response:
            if chunk.text:
                yield f"data: {json.dumps({'text': chunk.text})}\n\n"
        yield f"data: {json.dumps({'done': True})}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"


async def generate_report(db: Session) -> str:
    try:
        context = get_data_context(db)
        stats = get_full_stats(db)
        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = f"""Tu es un expert en qualité pharmaceutique. Génère un rapport APR (Annual Product Review) complet et professionnel.

DONNÉES DE L'USINE:
{context}

STATISTIQUES:
- Total lots produits: {stats['total_batches']}
- Dureté moyenne: {stats['avg_hardness']}N
- Rendement moyen: {stats['avg_yield']}%
- Taux de conformité QC: {stats['qc_pass_rate']}%
- Plaintes ouvertes: {stats['complaints_open']}
- CAPAs ouvertes: {stats['capas_open']}
- Équipements à calibrer: {stats['equipment_due']}
- Plaintes par catégorie: {stats['complaints_by_category']}
- Performance par machine: {stats['machines']}

Génère un rapport complet avec ces sections:

# RAPPORT ANNUEL DE REVUE PRODUIT (APR)
## Paracetamol 500mg - Année 2024

### 1. RÉSUMÉ EXÉCUTIF
(État général, conclusions clés)

### 2. PERFORMANCE DE PRODUCTION
- Volumes produits
- Rendements par période et par machine
- Analyse des tendances

### 3. CONTRÔLE QUALITÉ
- Résultats des tests (dissolution, essai, dureté, friabilité)
- Taux de conformité
- Non-conformités détectées

### 4. PLAINTES ET RÉCLAMATIONS
- Analyse par catégorie
- Tendances
- Actions correctives

### 5. ACTIONS CORRECTIVES ET PRÉVENTIVES (CAPA)
- CAPAs initiées
- Statut de clôture
- Efficacité

### 6. ÉQUIPEMENTS
- État de calibration
- Maintenance préventive

### 7. ANALYSE DES TENDANCES
- Dérives identifiées
- Signaux faibles
- Comparaison avec période précédente

### 8. CONCLUSIONS ET RECOMMANDATIONS
- Décision de maintien/modification du procédé
- Actions prioritaires pour l'année suivante

Sois précis, utilise les données chiffrées, et formate proprement en Markdown."""

        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Erreur lors de la génération du rapport: {str(e)}"
