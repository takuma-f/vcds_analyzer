import os
import re
import sys
import chardet
import pandas as pd

INPUT_DIR = "./org"
OUTPUT_DIR = "./data"

def extract_normalized_name(filename):
    """
    入力ファイル名から blockmap/adpmap と番号を抽出し、標準名に変換する
    例: blockmap-01-XXXXX.csv → blockmap-01.csv
    """
    match = re.match(r'^(blockmap|adpmap)-([A-Za-z0-9]+)', filename)
    if match:
        base, suffix = match.groups()
        return f"{base}-{suffix}.csv"
    return filename  # 規則外の名前はそのまま使う

def clean_csv(filename):
    input_path = os.path.join(INPUT_DIR, filename)
    output_filename = extract_normalized_name(filename)
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    with open(input_path, 'rb') as f:
        raw_data = f.read()
        detected_encoding = chardet.detect(raw_data)['encoding']

    print(f"[i] Encoding: {detected_encoding} | {filename} → {output_filename}")

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
                while len(parts) < 4:
                    parts.append(None)
                rows.append(parts)
            else:
                print(f"[!] Skipped line: {line}")

    if not rows:
        print(f"[!] No valid data rows found in {filename}")
        return

    df = pd.DataFrame(rows, columns=['Group', 'Description', 'Actual', 'Unit'])
    df['Unit'] = df['Unit'].replace({'�C': '°C', '�': ''}, regex=False)
    df['Actual'] = pd.to_numeric(df['Actual'], errors='coerce')
    df['Unit'] = df['Unit'].fillna('--')

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"[✓] Cleaned & saved to: {output_path}")

def batch_clean():
    files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith('.csv')]
    print(f"[i] Found {len(files)} CSV files.")
    for f in files:
        clean_csv(f)

def parse_diagscan(filename):
    input_path = os.path.join(INPUT_DIR, filename)
    with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()

    vehicle_info = {}
    module_status = []

    vin_match = re.search(r'VIN:\s+([A-Z0-9]+)', text)
    mileage_match = re.search(r'Mileage:\s+([0-9,]+km-[0-9,]+mi)', text)
    date_match = re.search(r'(\w+),(\d+),(\w+),(\d+),(\d+:\d+:\d+)', text)
    vcds_version = re.search(r'VCDS Version:\s+([\d\.]+)', text)

    if vin_match:
        vehicle_info['VIN'] = vin_match.group(1)
    if mileage_match:
        vehicle_info['Mileage'] = mileage_match.group(1)
    if date_match:
        vehicle_info['Date'] = f"{date_match.group(1)}, {date_match.group(2)} {date_match.group(3)} {date_match.group(4)} {date_match.group(5)}"
    if vcds_version:
        vehicle_info['VCDS Version'] = vcds_version.group(1)

    for line in text.splitlines():
        if re.match(r'^\d{2}-.*-- Status: ', line):
            parts = line.split('-- Status: ')
            if len(parts) == 2:
                module_status.append({
                    'Module': parts[0].strip(),
                    'Status': parts[1].strip()
                })

    print("[✓] Parsed Vehicle Info:", vehicle_info)
    print("[✓] Parsed Module Statuses:")
    for m in module_status:
        print(f"  - {m['Module']}: {m['Status']}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py [csv|diagscan] <optional_filename>")
        sys.exit(1)

    mode = sys.argv[1].lower()
    filename = sys.argv[2] if len(sys.argv) > 2 else None

    if mode == 'csv':
        if filename:
            clean_csv(filename)
        else:
            batch_clean()
    elif mode == 'diagscan':
        if not filename:
            print("[!] Please specify the diagscan filename.")
        else:
            parse_diagscan(filename)
    else:
        print(f"[!] Unknown mode: {mode}")