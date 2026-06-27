"""
Abbreviation expansion rules for institution names.
Maps short forms (ECB, MIT, BIS, etc.) to full institution names.
"""

ABBREVIATIONS = {
    # Central banks & international orgs
    r'\bECB\b':               'European Central Bank',
    r'\bBIS\b':               'Bank for International Settlements',
    r'\bIMF\b':               'International Monetary Fund',
    r'\bOECD\b':              'OECD',
    r'\bEBRD\b':              'European Bank for Reconstruction and Development',
    r'\bEIB\b':               'European Investment Bank',
    r'\bFRB\b':               'Federal Reserve Bank',
    r'\bBundesbank\b':        'Deutsche Bundesbank',

    # US universities
    r'\bMIT\b':               'Massachusetts Institute of Technology',
    r'\bNYU\b':               'New York University',
    r'\bUCLA\b':              'University of California, Los Angeles',
    r'\bUCSD\b':              'University of California, San Diego',
    r'\bUIUC\b':              'University of Illinois Urbana-Champaign',
    r'\bUNC\b':               'University of North Carolina',
    r'\bLSU\b':               'Louisiana State University',
    r'\bMSU\b':               'Michigan State University',
    r'\bASU\b':               'Arizona State University',
    r'\bHBS\b':               'Harvard Business School',
    r'\bCUNY\b':              'City University of New York',

    # UK / Europe universities
    r'\bLSE\b':               'London School of Economics and Political Science (LSE)',
    r'\bUCL\b':               'University College London',
    r'\bQMUL\b':              'Queen Mary University of London',
    r'\bKIT\b':               'Karlsruhe Institute of Technology',
    r'\bTUM\b':               'Technical University of Munich',
    r'\bNHH\b':               'NHH Norwegian School of Economics',
    r'\bNTU\b':               'Nanyang Technological University',
    r'\bNUS\b':               'National University of Singapore',

    # Research institutes
    r'\bCEMFI\b':             'CEMFI',
    r'\bCREST\b(?!\s+\()':    'CREST',
    r'\bCREI\b':              'Centre de Recerca en Economia Internacional',
    r'\bEIEF\b':              'Einaudi Institute for Economics and Finance',
    r'\bINSEAD\b':            'INSEAD',
    r'\bIAB\b':               'Institute for Employment Research (IAB)',
    r'\bIFN\b':              'Research Institute of Industrial Economics',
    r'\bPSE\b':               'Paris School of Economics',
    r'\bZEW\b':               'ZEW - Leibniz Centre for European Economic Research',
    r'\bDIW\b':               'DIW Berlin',

    # Asia
    r'\bHKU\b':               'The University of Hong Kong',
    r'\bHKUST\b':             'Hong Kong University of Science and Technology',
    r'\bCUHK\b':              'The Chinese University of Hong Kong',
    r'\bITAM\b':              'Instituto Tecnologico Autonomo de Mexico (ITAM)',

    # Canada
    r'\bUQAM\b':              'Universite du Quebec a Montreal',
    r'\bUBC\b':               'University of British Columbia',

    # Other
    r'\bVIVE\b':              'The Danish Center for Social Science Research (VIVE)',
    r'\bEPFL\b':              'Ecole Polytechnique Federale de Lausanne',
    r'\bEUI\b':               'European University Institute',
    r'\bLUISS\b':             'LUISS University',
    r'\bPUC\b':               'Pontificia Universidad Catolica de Chile',
}
