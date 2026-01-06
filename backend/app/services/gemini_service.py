import google.generativeai as genai
from app.config import GOOGLE_API_KEY
from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models
from datetime import datetime, timedelta
import json

genai.configure(api_key=GOOGLE_API_KEY)


def get_data_context(db: Session) -> str:
    """Build comprehensive context from all data sources"""
    batches = (
        db.query(models.Batch)
        .order_by(models.Batch.manufacturing_date.desc())
        .limit(50)
        .all()
    )
    qc_results = (
        db.query(models.QCResult)
        .order_by(models.QCResult.test_date.desc())
        .limit(50)
        .all()
    )
    complaints = db.query(models.Complaint).all()
    capas = db.query(models.CAPA).all()
    equipment = db.query(models.Equipment).limit(50).all()

    # Calculate statistics
    total_batches = db.query(models.Batch).count()
    avg_yield = db.query(func.avg(models.Batch.yield_percent)).scalar() or 0
    avg_hardness = db.query(func.avg(models.Batch.hardness)).scalar() or 0

    context = f"""
=== DONNÉES DE L'USINE PHARMACEUTIQUE - PARACETAMOL 500mg ===
Période analysée: 2020-2025 (6 ans de données APR)

📊 STATISTIQUES GLOBALES:
- Total lots produits: {total_batches:,}
- Rendement moyen: {avg_yield:.1f}%
- Dureté moyenne: {avg_hardness:.1f} kp
- Plaintes clients: {len(complaints)} ({len([c for c in complaints if c.status == 'open'])} ouvertes)
- CAPAs: {len(capas)} ({len([c for c in capas if c.status == 'open'])} ouvertes)

📦 LOTS RÉCENTS (derniers {len(batches)}):
"""
    for b in batches[:15]:
        date_str = (
            b.manufacturing_date.strftime("%Y-%m-%d") if b.manufacturing_date else "N/A"
        )
        context += f"- {b.batch_id}: {date_str}, Press: {b.tablet_press_id or 'N/A'}, Dureté: {b.hardness or 0:.1f}kp, Rendement: {b.yield_percent or 0:.1f}%\n"

    if qc_results:
        context += f"\n🔬 RÉSULTATS QC RÉCENTS ({len(qc_results)} tests):\n"
        for qc in qc_results[:15]:
            context += f"- {qc.batch_id}: Essai={qc.assay_percent or 0:.1f}%, Dissolution={qc.dissolution_mean or 0:.1f}%, Résultat: {qc.overall_result}\n"

    if complaints:
        context += f"\n📞 PLAINTES CLIENTS ({len(complaints)} total):\n"
        open_complaints = [
            c for c in complaints if c.status and c.status.lower() == "open"
        ]
        context += f"   Ouvertes: {len(open_complaints)}\n"
        by_category = {}
        for c in complaints:
            cat = c.category or "Autre"
            by_category[cat] = by_category.get(cat, 0) + 1
        for cat, count in sorted(by_category.items(), key=lambda x: -x[1])[:5]:
            context += f"   - {cat}: {count}\n"
        by_severity = {}
        for c in complaints:
            sev = c.severity or "Unknown"
            by_severity[sev] = by_severity.get(sev, 0) + 1
        context += f"   Par sévérité: {by_severity}\n"

    if capas:
        context += f"\n🔧 CAPAS ({len(capas)} total):\n"
        open_capas = [c for c in capas if c.status and "closed" not in c.status.lower()]
        context += f"   Ouvertes: {len(open_capas)}\n"
        by_source = {}
        for c in capas:
            src = c.source or "Autre"
            by_source[src] = by_source.get(src, 0) + 1
        for src, count in sorted(by_source.items(), key=lambda x: -x[1])[:5]:
            context += f"   - Source {src}: {count}\n"
        critical = [c for c in capas if c.risk_score == "Critical"]
        context += f"   CAPAs critiques: {len(critical)}\n"

    if equipment:
        context += f"\n⚙️ ÉQUIPEMENTS (calibrations récentes):\n"
        failures = [e for e in equipment if e.result == "Fail"]
        context += f"   Échecs de calibration: {len(failures)}\n"
        by_type = {}
        for e in equipment:
            t = e.equipment_type or "Autre"
            by_type[t] = by_type.get(t, 0) + 1
        context += f"   Par type: {by_type}\n"

    return context


SYSTEM_PROMPT = """Tu es NYOS, un assistant IA expert en qualité pharmaceutique et analyse APR (Annual Product Review).
Tu analyses les données de production de comprimés de Paracetamol 500mg sur une période de 6 ans (2020-2025).

Ton rôle:
1. Détecter les tendances et dérives dans les données de production
2. Identifier les anomalies, signaux faibles et problèmes potentiels
3. Analyser les corrélations entre équipements, lots, et résultats qualité
4. Résumer clairement la situation qualité de l'usine
5. Recommander des actions correctives et préventives

Scénarios cachés à détecter:
- 2020: Impact COVID-19 sur production
- 2021: Dégradation Press-A (Sept-Nov)
- 2022: Problème fournisseur excipient MCC (Juin)
- 2023: Transition méthode analytique (Q2)
- 2024: Effet température saisonnière (Juil-Août)
- 2025: Dérive Press-B + Nouveau fournisseur API (Nov)

Règles:
- Sois précis avec des données chiffrées
- Signale tout problème potentiel
- Réponds en français
- Utilise des bullet points et formatage markdown
- Cite les lots, dates et valeurs spécifiques quand pertinent
"""


async def chat_with_gemini(message: str, db: Session) -> str:
    try:
        context = get_data_context(db)
        model = genai.GenerativeModel("gemini-2.5-flash-lite")

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

    # Calculate QC pass rate based on actual pharmaceutical specifications
    # Specs: Assay 95-105%, Dissolution >80%
    qc_pass_count = len(
        [
            q
            for q in qc_results
            if q.assay_percent
            and q.dissolution_mean
            and 95 <= q.assay_percent <= 105
            and q.dissolution_mean >= 80
        ]
    )

    stats = {
        "total_batches": len(batches),
        "avg_hardness": (
            round(
                sum(b.hardness for b in batches if b.hardness)
                / max(len([b for b in batches if b.hardness]), 1),
                2,
            )
            if batches
            else 0
        ),
        "avg_yield": (
            round(
                sum(b.yield_percent for b in batches if b.yield_percent)
                / max(len([b for b in batches if b.yield_percent]), 1),
                2,
            )
            if batches
            else 0
        ),
        "machines": {},
        "qc_pass_rate": (
            round(qc_pass_count / max(len(qc_results), 1) * 100, 1) if qc_results else 0
        ),
        "complaints_by_category": {},
        "complaints_open": len(
            [c for c in complaints if c.status and c.status.lower() == "open"]
        ),
        "capas_open": len(
            [c for c in capas if c.status and "closed" not in c.status.lower()]
        ),
        "equipment_due": len([e for e in equipment if e.result == "Fail"]),
    }

    for b in batches:
        machine = b.tablet_press_id or "Unknown"
        if machine not in stats["machines"]:
            stats["machines"][machine] = {
                "count": 0,
                "hardness_sum": 0,
                "yield_sum": 0,
            }
        stats["machines"][machine]["count"] += 1
        stats["machines"][machine]["hardness_sum"] += b.hardness or 0
        stats["machines"][machine]["yield_sum"] += b.yield_percent or 0

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
        model = genai.GenerativeModel("gemini-2.5-flash-lite")

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
