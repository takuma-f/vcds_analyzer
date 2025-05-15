import os
import io
import pandas as pd
import chardet

# 入出力ディレクトリのパス設定
INPUT_DIR = "./org"
OUTPUT_DIR = "./data"

def detect_encoding(file_path):
    # 文字コード自動検出
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    return result['encoding']

def clean_csv(filename):
    input_path = os.path.join(INPUT_DIR, filename)
    output_path = os.path.join(OUTPUT_DIR, filename)

    # ファイルのエンコーディングを推測
    with open(input_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        detected_encoding = result['encoding']

    print(f"[i] Detected encoding for {filename}: {detected_encoding}")

    # 有効なデータ行だけ取り出す
    rows = []
    with open(input_path, 'r', encoding=detected_encoding, errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith(';'):
                continue
            parts = line.split(',')
            if parts[0] == 'Group' and parts[1] == 'Description':
                continue
            if 2 <= len(parts) <= 4:
                # 足りない列はNoneで補完
                while len(parts) < 4:
                    parts.append(None)
                rows.append(parts)
            else:
                print(f"[!] Skipped line (unexpected columns): {line}")

    if not rows:
        print(f"[!] No valid data rows found in {filename}.")
        return

    # DataFrame化
    df = pd.DataFrame(rows, columns=['Group', 'Description', 'Actual', 'Unit'])

    # 単位の文字化け修正
    df['Unit'] = df['Unit'].replace({'�C': '°C', '�': ''}, regex=False)

    # 数値化（失敗したらNaNに）
    df['Actual'] = pd.to_numeric(df['Actual'], errors='coerce')

    # 単位未記載を補完
    df['Unit'] = df['Unit'].fillna('--')

    # 保存
    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"[✓] Cleaned: {input_path} → {output_path}")


def batch_clean():
    # .csv or .CSV 拡張子のファイルを全取得
    files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".csv")]
    print(f"[i] Found {len(files)} files: {files}")
    for file in files:
        clean_csv(file)

if __name__ == "__main__":
    batch_clean()
