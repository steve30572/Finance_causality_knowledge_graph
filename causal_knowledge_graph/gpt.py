import pandas as pd
from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()
import json
import time
from openai import OpenAI
from tqdm import tqdm

def make_batch_prompt(prompt_version, data_frame):
    """
    rows: list of dicts, where each dict has keys:
          ['idx', 'date', 'actor1', 'actor2', 'event_code', 'event_desc']
    """
    
    # 1. 리스트에 있는 모든 사건을 하나의 문자열로 변환
    events_text = ""
    for index, row in data_frame.iterrows():
        events_text += (
            f"Index: {index} | "
            f"Date: {row['date']} | "
            f"Actors: {row['actor1']} -> {row['actor2']} | "
            f"Event: {row['event_desc']} (Code: {row['event_code']})\n"
        )

    # 2. 프롬프트 구성 (영어 번역 및 지침 포함)
    with open(f"prompts/{prompt_version}.txt", "r", encoding="utf-8") as f:
        prompt = f.read()
        
    prompt = prompt.replace("{events_text}", events_text)
    
    return prompt


data_type = "usa"  # "2012"
data = pd.read_parquet(f"df_filtered_{data_type}_final.parquet")
out_dir = Path(".")
prompt_version = "v7"
number_of_samples = 2000
temperature = 0.0
MODEL = "gpt-4.1-nano"

# for문 시작
results = []
for num_iter in tqdm(range(100)):
    sampled = data.sample(n=number_of_samples, random_state=num_iter)
    # convert date to datetime (YYYYMMDD) and sort sampled ascending by date
    sampled['date'] = pd.to_datetime(sampled['date'], format='%Y%m%d', errors='coerce')
    sampled = sampled.sort_values('date', ascending=True)
    sampled['date'] = sampled['date'].dt.strftime('%Y-%m-%d')

    prompts = make_batch_prompt(prompt_version, sampled)

    # save prompts to a text file (one prompt per block)
    prompts_file = out_dir / "prompts" / f"{data_type}-{MODEL}-prompt-{prompt_version}-{number_of_samples}-{temperature}.txt"
    with prompts_file.open("w", encoding="utf-8") as f:
        f.write(prompts)
        
        
        
    # Optional: call OpenAI API if available
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

    if OPENAI_API_KEY is None:
        print("OPENAI_API_KEY not found in environment. Skipping API calls.")
    else:
        try:
            import openai
        except Exception as e:
            print("openai package not installed or failed to import:", e)
            openai = None
            
            
        client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY")
        )
        
        if openai is not None:
            openai.api_key = OPENAI_API_KEY
            # adjust model and rate settings as needed
            delay_between_calls = 1.0  # seconds

            prompt_text = prompts
            
            try:
                if MODEL.startswith("gpt-5"):
                    resp = client.chat.completions.create(
                            model=MODEL,  # 또는 사용 중인 모델명
                            messages=[{"role": "user", "content": prompt_text}],
                            max_completion_tokens=2048, # JSON이 길어질 수 있으므로 넉넉하게 잡는 것을 추천
                        )
                else:
                    resp = client.chat.completions.create(
                            model=MODEL,  # 또는 사용 중인 모델명
                            messages=[{"role": "user", "content": prompt_text}],
                            max_tokens=2048, # JSON이 길어질 수 있으므로 넉넉하게 잡는 것을 추천
                            temperature=temperature,
                        )
                    
                # 4. 응답 접근 방식 변경: 딕셔너리([])가 아니라 점(.)으로 접근
                content = resp.choices[0].message.content.strip()
            except Exception as e:
                content = f"__error__: {e}"
            # attempt to parse JSON from the reply
            parsed = None
            if not content.startswith("__error__"):
                # try to find first JSON array in the text
                try:
                    # naive extraction: find first '[' and last ']' and parse
                    start = content.find('[')
                    end = content.rfind(']')
                    if start != -1 and end != -1 and end > start:
                        json_text = content[start:end+1]
                        parsed = json.loads(json_text)
                except Exception:
                    parsed = None

            results.append({
                "prompt": prompt_text,
                "response_text": content,
                "parsed_json": parsed,
            })

            # simple pacing
            time.sleep(delay_between_calls)

# save responses to file
out_file = out_dir / "results" / f"{data_type}-{MODEL}-{prompt_version}-{number_of_samples}-{temperature}-100_gpt_responses.jsonl"
with out_file.open("w", encoding="utf-8") as f:
    for r in results:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
        
print(f"Saved {len(results)} responses to {out_file}")