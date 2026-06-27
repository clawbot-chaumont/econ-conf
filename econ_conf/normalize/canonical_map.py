"""
Canonical institution name mappings.

Key = raw institution name as it appears after basic cleaning (diacritics stripped,
abbreviations expanded, trailing punctuation removed).
Value = canonical institution name to use in the final output.

Add new entries here as new variants are discovered.
"""

CANONICAL_MAP = {
    # ── Federal Reserve ──────────────────────────────────────────────────
    'Board of Governors of the Federal Reserve System':  'Federal Reserve Bank',
    'Board of Governors of the Federal Reserv':           'Federal Reserve Bank',
    'Federal Reserve Board':                              'Federal Reserve Bank',
    'Federal Reserve Board, USA':                         'Federal Reserve Bank',
    'Federal Reserve Board of Governors':                 'Federal Reserve Bank',
    'Federal Reserve Board of Governors, USA':            'Federal Reserve Bank',
    'Federal Reserve System':                             'Federal Reserve Bank',
    'federal reserve bank of saint louis':                'Federal Reserve Bank of St. Louis',
    'Federal reserve Bank of Philadelphia':               'Federal Reserve Bank of Philadelphia',
    'Federal Reserve Bank of Saint Louis':                'Federal Reserve Bank of St. Louis',
    'Federal Reserve Bank of Minneapolis and NBER':       'Federal Reserve Bank of Minneapolis',
    'Federal Reserve New York':                           'Federal Reserve Bank of New York',

    # ── Bank of Canada ───────────────────────────────────────────────────
    'Bank of Canada / Banque du Canada': 'Bank of Canada',

    # ── University of Chicago ────────────────────────────────────────────
    'University of Chicago Booth School of':                 'University of Chicago Booth School of Business',
    'Booth School of Business, University of Chicago':       'University of Chicago Booth School of Business',

    # ── Wharton ──────────────────────────────────────────────────────────
    'The Wharton School, University of Pennsylvania':         'Wharton School, University of Pennsylvania',
    'The Wharton School at University of Pennsylvania':       'Wharton School, University of Pennsylvania',
    'The Wharton School of the University of Pennsylvania':   'Wharton School, University of Pennsylvania',
    'University of Pennsylvania - The Wharton School':        'Wharton School, University of Pennsylvania',
    'Wharton School, University of Pennsylvania; NBER':       'Wharton School, University of Pennsylvania',
    'The Wharton School, University of Pennsylvania and NBER': 'Wharton School, University of Pennsylvania and NBER',

    # ── Paris Dauphine ───────────────────────────────────────────────────
    'Universite Paris Dauphine-PSL':      'Universite Paris Dauphine-PSL',
    'Universite Paris Dauphine - PSL':    'Universite Paris Dauphine-PSL',
    'Universite Paris Dauphine':          'Universite Paris Dauphine-PSL',
    'University Paris Dauphine-PSL':      'Universite Paris Dauphine-PSL',
    'Paris Dauphine University':          'Universite Paris Dauphine-PSL',
    'Paris Dauphine-PSL University':      'Universite Paris Dauphine-PSL',
    'Paris Dauphine - Psl':               'Universite Paris Dauphine-PSL',
    'Paris Dauphine PSL':                 'Universite Paris Dauphine-PSL',
    'Dauphine-PSL':                       'Universite Paris Dauphine-PSL',
    'Universite Paris Dauphine - PSL, DRM- Finance': 'Universite Paris Dauphine-PSL',
    "Laboratoire d'Economie de Dauphine, Chaire Economie du Climat": 'Universite Paris Dauphine-PSL',
    'university paris-dauphine-PSL':      'Universite Paris Dauphine-PSL',

    # ── Paris-Saclay ─────────────────────────────────────────────────────
    'Universite Paris-Saclay':            'Universite Paris-Saclay',
    'University Paris-Saclay':            'Universite Paris-Saclay',
    'Universite Evry Paris-Saclay':       'Universite Paris-Saclay',
    'University of Evry Paris-Saclay':    'Universite Paris-Saclay',
    'ENS Paris-Saclay':                   'Universite Paris-Saclay',
    'CentraleSupelec/Universite Paris-Saclay': 'Universite Paris-Saclay',
    'University Evry Paris-':             'Universite Paris-Saclay',
    'University Paris-Est':               'Universite Paris-Est Creteil',
    'Universite Paris-Est Creteil':       'Universite Paris-Est Creteil',

    # ── Paris 1 Pantheon-Sorbonne ────────────────────────────────────────
    'Universite Paris 1 Pantheon-Sorbonne':  'Universite Paris 1 Pantheon-Sorbonne',
    'Universite Paris 1 - Pantheon Sorbonne': 'Universite Paris 1 Pantheon-Sorbonne',
    'Universite Paris 1 Pantheon Sorbonne': 'Universite Paris 1 Pantheon-Sorbonne',
    'Paris 1 Pantheon-Sorbonne':           'Universite Paris 1 Pantheon-Sorbonne',
    'Paris 1, Pantheon-Sorbonne':          'Universite Paris 1 Pantheon-Sorbonne',
    'CES - Universite Paris 1 Pantheon-Sorbonne': 'Universite Paris 1 Pantheon-Sorbonne',
    "Universite Paris 1 Pantheon-Sorbonne - Ecole d'economie de la Sorbonne": 'Universite Paris 1 Pantheon-Sorbonne',
    'Sorbonne Economics Center (Pantheon-Sorbonne Paris 1 University)': 'Universite Paris 1 Pantheon-Sorbonne',
    'Sorbonne Economics Center (Pantheon-Sorbonne Paris 1 University), France CFEN: Asset Pricing II': 'Universite Paris 1 Pantheon-Sorbonne',
    "Centre d'Economie de la Sorbonne":    'Universite Paris 1 Pantheon-Sorbonne',
    "Centre d'economie de la Sorbonne":    'Universite Paris 1 Pantheon-Sorbonne',
    'IAE Paris - Sorbonne Business School': 'Universite Paris 1 Pantheon-Sorbonne',
    'IAE Paris - Sorbonne Business School, France': 'Universite Paris 1 Pantheon-Sorbonne',

    # ── Paris-Pantheon-Assas ────────────────────────────────────────────
    'Universite Paris-Pantheon-Assas':     'Universite Paris-Pantheon-Assas',
    'Universite Paris Pantheon-Assas':     'Universite Paris-Pantheon-Assas',
    'University Paris 8':                  'Universite Paris 8',

    # ── Paris Nanterre ───────────────────────────────────────────────────
    'Universite Paris Nanterre':           'Universite Paris Nanterre',
    'Universite Paris Nanterre - EconomiX':'Universite Paris Nanterre',

    # ── Paris School of Economics ────────────────────────────────────────
    'Paris School of Economics/INSEE':              'Paris School of Economics',
    'Paris School of Economics-CNRS':               'Paris School of Economics',
    'Paris School of Economics / Banque de France': 'Paris School of Economics',
    'Paris School of Economics, College de France': 'Paris School of Economics',
    'PSE, College de France':                       'Paris School of Economics',
    'Paris School of  Economics':                   'Paris School of Economics',
    'Professor of Economics at the Paris School of Economics, EHESS': 'Paris School of Economics',

    # ── HEC ──────────────────────────────────────────────────────────────
    'HEC - Paris':                    'HEC Paris',
    'HEC School of Management':       'HEC Paris',
    'HEC - Montreal':                 'HEC Montreal',
    'HEC - MontrA©al':               'HEC Montreal',
    'HEC montreal':                   'HEC Montreal',
    'HEC Montreal, Canada CMSG: Macroeconomic Policy / Politique macroeconomique': 'HEC Montreal',
    'HEC Montreal, Canada Urban, Regional, and Spatial Economics: Media, Attention, and Digital Technology': 'HEC Montreal',
    'HEC - Lausanne':                 'HEC Lausanne',
    'HEC- University of Lausanne':    'HEC Lausanne',

    # ── EDHEC ─────────────────────────────────────────────────────────────
    'Edhec Business School':          'EDHEC Business School',
    'EDHEC':                          'EDHEC Business School',
    'Scientific Portfolio an EDHEC venture': 'EDHEC Business School',

    # ── ENSAE = CREST - IP Paris ─────────────────────────────────────────
    'Ensae':                          'CREST - IP Paris',
    'ENSAE':                          'CREST - IP Paris',

    # ── CY Cergy ─────────────────────────────────────────────────────────
    'CY Cergy Paris Universite - Thema':        'CY Cergy Paris Universite',
    'CY Cergy Paris University THEMA (France)': 'CY Cergy Paris Universite',
    'Cergy Paris Universite':                   'CY Cergy Paris Universite',

    # ── Other French ─────────────────────────────────────────────────────
    'Sciences Po, Paris':                      'Sciences Po',
    'CREST - Institut Polytechnique de Paris': 'CREST - IP Paris',
    'BNP Parisbas':                            'BNP Paribas',
    'Universite Paris-':                       'Universite Paris-Pantheon-Assas',

    # ── St. Gallen ───────────────────────────────────────────────────────
    'University of St. Gallen, Switzerland': 'University of St. Gallen',

    # ── Aix-Marseille ────────────────────────────────────────────────────
    'Aix-Marseille Universite': 'Aix-Marseille University',

    # ── European universities (name variants) ────────────────────────────
    'Pompeu Fabra University':      'Universitat Pompeu Fabra',
    'Warsaw School of Economics':   'SGH Warsaw School of Economics',
    'University of Maastricht':     'Maastricht University',
    'Universitat Leipzig':          'Leipzig University',
    'University of Leipzig':        'Leipzig University',
    "Universite d'Orleans":         "Universite d'Orleans",
    "Universite D'orleans":         "Universite d'Orleans",
    "Universite d'Orleans":         "Universite d'Orleans",

    # ── LSE ──────────────────────────────────────────────────────────────
    'London School of Economics and Political Science': 'London School of Economics and Political Science (LSE)',
    'London School of Economics':                       'London School of Economics and Political Science (LSE)',

    # ── Swiss Finance ────────────────────────────────────────────────────
    'Swiss Finance Institute - EPFL': 'Swiss Finance Institute',

    # ── CEMFI ────────────────────────────────────────────────────────────
    'Center For Monetary And Financial Studies (CEMFI)': 'CEMFI',
    'Center for Monetary and Financial Studies':          'CEMFI',

    # ── Hyphenation / typo variants ──────────────────────────────────────
    'Bar Ilan University':                      'Bar-Ilan University',
    'Ben Gurion University':                    'Ben-Gurion University',
    'Carnegie-Mellon University':               'Carnegie Mellon University',
    'banque de france':                         'Banque de France',
    'banco do portugal':                        'Banco de Portugal',
    'IESE Business School; University of Navarra': 'IESE Business School',
    'Simon Fraser Univeristy, Canada':          'Simon Fraser University',
    "Saint Mary's Universtiy, Canada":          "Saint Mary's University, Canada",
    'University of Amstedam':                   'University of Amsterdam',
    'Massachusetts Institute of Techonology':   'Massachusetts Institute of Technology',
    'Deustche Bundesbank':                      'Deutsche Bundesbank',
    'Deutsche Budesbank':                       'Deutsche Bundesbank',
    'Univeristy College Dublin':                'University College Dublin',
    'University College ublin':                 'University College Dublin',
    'Universita Bocconi':                       'Bocconi University',
    'John Hopkins University':                  'Johns Hopkins University',
    'Univerity of Oxford':                      'University of Oxford',
    'Tel Aviv Univesity':                       'Tel Aviv University',
    'Darmouth College and NBER':                'Dartmouth College and NBER',
    'ifo Insitute':                             'ifo Institute',
    'Binghampton University':                   'Binghamton University',
    'Institute for Employment Reserach':        'Institute for Employment Research (IAB)',
    'CUNY-Graduate Center':                     'City University of New York Graduate Center',
    'CUNY Graduate Center':                     'City University of New York Graduate Center',
    'The Graduate Center, CUNY':                'City University of New York Graduate Center',
}
