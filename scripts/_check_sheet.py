#!/usr/bin/env python3
import json, os
from google.oauth2.credentials import Credentials
import gspread

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds = Credentials.from_authorized_user_file(os.path.expanduser('~/.hermes/google_token.json'), SCOPES)
gc = gspread.authorize(creds)
sh = gc.open_by_key('17sfWz82YgaoK6_Kznv1SNXTOO55RuuwCDMJ6RT3ZYgw')
ws = sh.worksheet('Conferences')

rows = ws.get_all_values()
header = rows[0]
print("Columns checklist:")
interesting_cols = [(0,"Name"),(1,"Short"),(2,"Year"),(3,"FullName"),(5,"Website"),
                    (15,"Status"),(16,"Type"),(22,"Start"),(23,"End"),(31,"City"),
                    (39,"CheckDate")]
for idx, name in interesting_cols:
    v = header[idx] if idx < len(header) else "???"
    print(f"  Col {idx} ({name}): {v}")

print()

# Past conferences
past_keys = ['AEA','AFA','DES','3CMFI','BFSR','SSFMR','SFS','MYE','AFFI','RCEA','ICMAIF','CEA','JMA','SFWFIR','BWBFI']

all_rows = rows[1:]
for row in all_rows:
    key = row[1].strip().upper()
    if key in past_keys:
        name = row[3][:35] if len(row) > 3 else ""
        website = row[5][:40] if len(row) > 5 else ""
        status = row[15] if len(row) > 15 else ""
        typ = row[16] if len(row) > 16 else ""
        start = row[22] if len(row) > 22 else ""
        end = row[23] if len(row) > 23 else ""
        city = row[31] if len(row) > 31 else ""
        check = row[39] if len(row) > 39 else ""
        print(f"{key:7s} | {start:12s}→{end:12s} | stat={status:8s} | type={typ:8s} | city={city:15s} | check={check:12s} | {name}")
