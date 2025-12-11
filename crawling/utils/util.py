import pandas as pd
import requests, zipfile, os
from tqdm import tqdm
from datetime import datetime, timedelta

# URL Example
# BASE_URL = "http://data.gdeltproject.org/gdeltv2/"
# MASTER_LIST_URL = "http://data.gdeltproject.org/gdeltv2/masterfilelist.txt"

def get_available_files(base_url ,list_url, days=1):
    """
    masterfilelist에서 파일명 기반 timestamp 추출 후,
    최근 days일치 export CSV만 반환
    """
    print("[INFO] masterfilelist 다운로드 중…")
    r = requests.get(base_url + list_url)
    lines = r.text.strip().split("\n")

    records = []
    for line in lines:
        parts = line.split(" ")
        if len(parts) != 3:
            continue

        md5, size, fname = parts

        # export.CSV.zip 파일만 선택
        if not fname.endswith("export.CSV.zip"):
            continue

        # 파일명에서 http://data.gdeltproject.org/gdeltv2/ 지우기
        fname = fname.replace(base_url, "")
        # 파일명에서 timestamp 추출
        # 예: http://data.gdeltproject.org/gdeltv2/20250226121500.export.CSV.zip → 20250226121500
        ts_str = fname.split(".")[0]

        try:
            ts = pd.to_datetime(ts_str, format="%Y%m%d%H%M%S", utc=True)
        except:
            continue

        records.append({
            "filename": fname,
            "timestamp": ts
        })

    df = pd.DataFrame(records)

    cutoff = pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=days)
    df = df[df["timestamp"] >= cutoff]

    return df["filename"].tolist()


def download_gdelt_files(days=1, out_dir="gdelt_raw"):
    os.makedirs(out_dir, exist_ok=True)

    fnames = get_available_files(days)
    print(f"[INFO] 다운로드 대상 파일 수: {len(fnames)}")

    downloaded = []

    for fname in tqdm(fnames):
        url = f"http://data.gdeltproject.org/gdeltv2/{fname}"
        out_path = os.path.join(out_dir, fname)

        if os.path.exists(out_path):
            downloaded.append(out_path)
            continue

        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                with open(out_path, "wb") as f:
                    f.write(r.content)
                downloaded.append(out_path)
        except:
            pass

    print(f"[INFO] 다운로드 완료: {len(downloaded)}개 파일")
    return downloaded

def extract_economic_events(df, ECONOMIC_EVENTCODES):
    """경제 EventCode만 선택하고 datetime & actor 정리"""
    df = df[df["col_26"].astype(str).isin(ECONOMIC_EVENTCODES)]

    # 날짜 처리
    df["datetime"] = pd.to_datetime(df["col_1"], format="%Y%m%d", errors="coerce")

    # Actor1/Actor2 (간단 버전)
    df["actor1"] = df["col_5"].fillna("") + "|" + df["col_6"].fillna("")
    df["actor2"] = df["col_15"].fillna("") + "|" + df["col_16"].fillna("")

    # URL ( 뉴스 원문 링크 )
    df["url"] = df["col_60"]

    return df
