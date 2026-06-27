#!/usr/bin/env python3
"""
Scraper pour WFA (Western Finance Association) 2026.

Le programme WFA est hébergé sur un portail avec authentification :
  https://westernfinance-portal.org/conference

Ce scraper ne peut pas accéder au programme sans credentials.
Le programme est accessible en naviguant sur le portail après connexion.

Pour obtenir le programme :
1. Aller sur https://westernfinance.org/conference-2026/
2. Suivre le lien vers le portail des sessions
3. Récupérer les données manuellement via le portail

Output: data.json (format v2)
"""

import json, os, sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from pipeline.master_pipeline import convert_to_v2

def scrape():
    """Retourne les données brutes pour conversion."""
    return {
        "conference": "Western Finance Association Annual Meeting",
        "scrape_date": datetime.now().isoformat(),
        "sessions": [],
        "participants": [],
        "program_available": True,
        "notes": "Programme accessible via portail authentifié: https://westernfinance-portal.org/conference"
    }

if __name__ == "__main__":
    data = scrape()
    output = convert_to_v2("WFA", data)
    out_path = os.path.join(os.path.dirname(__file__), "data.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"✅ WFA data.json écrit ({len(output.get('sessions', []))} sessions, {len(output.get('participants', []))} participants)")
