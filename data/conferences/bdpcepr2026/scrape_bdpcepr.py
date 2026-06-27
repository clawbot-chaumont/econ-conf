#!/usr/bin/env python3
"""
Scraper pour Banco de Portugal & CEPR Conference on Financial Intermediation 2026.

Site CEPR protégé par Cloudflare — scraping automatisé non possible.
Le programme est probablement disponible en PDF sur la page :
  https://cepr.org/events/banco-de-portugal-and-cepr-conference-financial-intermediation-2026

Pour obtenir le programme :
1. Naviguer sur la page CEPR (nécessite un navigateur)
2. Télécharger le PDF du programme s'il est disponible
3. Extraire les sessions/participants du PDF

Output: data.json (format v2)
"""

import json, os, sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from pipeline.master_pipeline import convert_to_v2

def scrape():
    """Retourne les données brutes pour conversion."""
    return {
        "conference": "Banco de Portugal and CEPR Conference on Financial Intermediation",
        "scrape_date": datetime.now().isoformat(),
        "sessions": [],
        "participants": [],
        "program_available": True,
        "notes": "Site CEPR protégé par Cloudflare; programme PDF à télécharger manuellement depuis la page CEPR"
    }

if __name__ == "__main__":
    data = scrape()
    output = convert_to_v2("BDPCEPR", data)
    out_path = os.path.join(os.path.dirname(__file__), "data.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"✅ BdP-CEPR data.json écrit ({len(output.get('sessions', []))} sessions, {len(output.get('participants', []))} participants)")
