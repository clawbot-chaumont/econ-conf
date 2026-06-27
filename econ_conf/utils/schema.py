"""
Schema validation utilities for the v2 conference data format.
"""

import json

REQUIRED_CONFERENCE_FIELDS = ['name', 'short_name', 'year']
REQUIRED_SESSION_FIELDS = ['session_title', 'papers']
REQUIRED_PAPER_FIELDS = ['title', 'authors']
REQUIRED_PARTICIPANT_FIELDS = ['name', 'institution', 'is_presenter', 'papers']


def validate_v2(data: dict, path: str = "") -> list:
    """Validate a data.json against the v2 schema. Returns list of errors."""
    errors = []

    # conference
    conf = data.get('conference', {})
    if isinstance(conf, str):
        errors.append(f"{path}: 'conference' is a string, must be a dict")
    else:
        for f in REQUIRED_CONFERENCE_FIELDS:
            if f not in conf:
                errors.append(f"{path}: conference missing field '{f}'")

    # scrape_metadata
    meta = data.get('scrape_metadata', {})
    if not isinstance(meta, dict):
        errors.append(f"{path}: 'scrape_metadata' missing or not a dict")

    # sessions
    sessions = data.get('sessions', [])
    if not isinstance(sessions, list):
        errors.append(f"{path}: 'sessions' is not a list")
    else:
        for i, sess in enumerate(sessions):
            for f in REQUIRED_SESSION_FIELDS:
                if f not in sess:
                    errors.append(f"{path}: sessions[{i}] missing '{f}'")
            papers = sess.get('papers', [])
            if not isinstance(papers, list):
                errors.append(f"{path}: sessions[{i}].papers is not a list")
            for j, paper in enumerate(papers):
                for pf in REQUIRED_PAPER_FIELDS:
                    if pf not in paper:
                        errors.append(f"{path}: sessions[{i}].papers[{j}] missing '{pf}'")
                authors = paper.get('authors', [])
                if not isinstance(authors, list):
                    errors.append(f"{path}: sessions[{i}].papers[{j}].authors is not a list")

    # participants
    participants = data.get('participants', [])
    if not isinstance(participants, list):
        errors.append(f"{path}: 'participants' is not a list")
    else:
        for i, p in enumerate(participants):
            if 'name' not in p:
                errors.append(f"{path}: participants[{i}] missing 'name'")
            inst = p.get('institution', None)
            if inst is None:
                errors.append(f"{path}: participants[{i}] has null institution")
            papers_field = p.get('papers', p.get('paper_titles', []))
            if not isinstance(papers_field, list):
                errors.append(f"{path}: participants[{i}].papers is not a list")

    return errors
