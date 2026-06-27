"""Google Drive upload and sharing utilities."""
# See the google-workspace skill for the full GAPI wrapper.
# Path: ~/.hermes/skills/productivity/google-workspace/scripts/google_api.py

import subprocess
import json

GAPI = [
    'python3',
    os.path.expanduser('~/.hermes/skills/productivity/google-workspace/scripts/google_api.py'),
]


def upload(file_path: str, name: str = None, parent: str = None) -> dict:
    """Upload a file to Google Drive. Returns {id, name, webViewLink}."""
    cmd = GAPI + ['drive', 'upload', file_path]
    if name:
        cmd += ['--name', name]
    if parent:
        cmd += ['--parent', parent]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Upload failed: {result.stderr}")
    return json.loads(result.stdout)


def search(query: str, max_results: int = 20) -> list:
    """Search for files on Google Drive."""
    cmd = GAPI + ['drive', 'search', query, '--max', str(max_results)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Search failed: {result.stderr}")
    return json.loads(result.stdout)
