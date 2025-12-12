import pandas as pd
import re
from datetime import datetime

# 데이터 로드
data_path = ""
df = pd.read_csv(data_path)

# 1. 날짜 처리 함수
def get_date_object(text):
    match = re.search(r'(\d{8})', str(text))
    if match:
        return datetime.strptime(match.group(1), '%Y%m%d')
    return None

# 2. 단어 유사도 계산 함수 (Jaccard Similarity)
def get_jaccard_similarity(str1, str2):
    # 불용어(의미 없는 단어) 제거
    stop_words = set(['to', 'on', 'for', 'of', 'in', 'the', 'a', 'an', 'at', 'by', 'regarding', 'intent'])
    
    # 전처리: 소문자 변환, 숫자 제거, 단어 추출
    def clean_and_tokenize(text):
        text = re.sub(r'\d+', '', str(text)).lower()
        tokens = set(re.findall(r'\b[a-zA-Z]{3,}\b', text)) # 3글자 이상만
        return tokens - stop_words

    set1 = clean_and_tokenize(str1)
    set2 = clean_and_tokenize(str2)
    
    if not set1 or not set2:
        return 0.0
    
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    return intersection / union

 def main():
    # --- 평가 로직 실행 ---

    # 1단계: 기본 데이터 계산 (날짜 차이, 유사도 점수)
    date_diffs = []
    similarities = []

    for index, row in df.iterrows():
        c_date = get_date_object(row['cause'])
        e_date = get_date_object(row['effect'])

        # 날짜 차이 계산 (일 단위)
        if c_date and e_date:
            diff = (e_date - c_date).days
        else:
            diff = -999 # 날짜 없음
        date_diffs.append(diff)

        # 유사도 계산
        sim = get_jaccard_similarity(row['cause'], row['effect'])
        similarities.append(sim)

    df['days_diff'] = date_diffs
    df['similarity_score'] = similarities

    # 2단계: 0과 1을 가르는 임계값(Threshold) 설정
    # 하위 10% 정도를 잘라내기 위해 유사도 하위 10% 지점 확인
    sim_threshold = df['similarity_score'].quantile(0.10)

    def final_evaluation(row):
        # Condition 1: 시간 역행 (기본 오류) -> 0
        if row['days_diff'] != -999 and row['days_diff'] < 0:
            return 0

        # Condition 2: 유효 기간 만료 (60일 이상 경과) -> 0
        # (너무 오래된 과거의 일이 원인이라고 주장하는 경우)
        if row['days_diff'] > 60:
            return 0

        # Condition 3: 문맥 유사도 너무 낮음 (하위 10% 미만) -> 0
        # (두 문장의 내용이 너무 동떨어져 있음)
        if row['similarity_score'] < sim_threshold:
            return 0

        # 그 외에는 모두 1 (약 90% 목표)
        return 1

    df['evaluation'] = df.apply(final_evaluation, axis=1)

    # 결과 통계 확인
    print("Evaluation 분포:")
    print(df['evaluation'].value_counts(normalize=True))

    # CSV 저장
    df_final = df.drop(columns=['days_diff', 'similarity_score']) # 계산용 열 제거
    df_final.to_csv('stacked_cause_effect_evaluated_90_10.csv', index=False)

    print("\n상위 5개 데이터 확인:")
    print(df_final.head())
    # Check count and ratio of 1's in evaluation column of df_final
    total = len(df_final)
    if total == 0:
        print("데이터프레임이 비어있습니다.")
    else:
        ones = int(df_final['evaluation'].sum())
        ratio = ones / total
        print(f"Evaluation=1 개수: {ones} / {total} ({ratio:.4f} -> {ratio*100:.2f}%)")

    # Find the rows where evaluation is 0
    df_zeros = df_final[df_final['evaluation'] == 0]
    print(f"\nEvaluation=0 개수: {len(df_zeros)}")

    return 0

if __name__ == '__main__':
    main()
