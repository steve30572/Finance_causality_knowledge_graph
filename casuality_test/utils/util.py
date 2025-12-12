import pandas as pd
import re
from datetime import datetime

# 1. 날짜 처리 함수
def get_date_object(text):
    match = re.search(r'(\d{8})', str(text))
    if match:
        return datetime.strptime(match.group(1), '%Y%m%d')
    return None
