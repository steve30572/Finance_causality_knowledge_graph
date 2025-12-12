import pandas as pd
import re
import csv
import json

from datetime import datetime


# 1. 날짜 처리 함수
def get_date_object(text):
    match = re.search(r'(\d{8})', str(text))
    if match:
        return datetime.strptime(match.group(1), '%Y%m%d')
    return None

def csv_to_json(csv_path, json_path=None):
    data = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)

    # Optionally save to file
    if json_path:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    return data
