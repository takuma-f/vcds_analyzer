import os
import glob
import yaml
import pandas as pd
import markdown
import pdfkit
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional

# ===== 設定ファイルの読み込み =====
def load_config(config_path: str) -> Dict:
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

# ===== ファイル探索 & 読み込み =====
def find_file(directory: str, keyword: str) -> Optional[str]:
    pattern = os.path.join(directory, f"*{keyword}*.csv")
    matches = glob.glob(pattern)
    print(f"[DEBUG] Searching for '{keyword}' in '{directory}' → Matches: {matches}")
    return matches[0] if matches else None

def load_csv(path: str) -> pd.DataFrame:
    print(f"[DEBUG] Loading CSV from path: {path}")
    if not os.path.exists(path):
        print(f"[ERROR] File not found: {path}")
        return pd.DataFrame()

    try:
        df = pd.read_csv(path, encoding='utf-8')
        print(f"[DEBUG] CSV loaded: {path}")
        print(f"[DEBUG] Columns: {df.columns.tolist()}")
        print(f"[DEBUG] First 5 rows:\n{df.head()}")
        if df.empty:
            print(f"[WARNING] DataFrame from {path} is empty.")
        return df
    except Exception as e:
        print(f"[ERROR] Failed to read {path}: {e}")
        return pd.DataFrame()

# ===== データ構造の定義 =====
@dataclass
class Measurement:
    group: str
    description: str
    actual: str
    unit: str

@dataclass
class ParsedData:
    blockmap_by_module: Dict[str, List[Measurement]] = field(default_factory=dict)
    adaptation_by_module: Dict[str, List[Measurement]] = field(default_factory=dict)

# ===== データの構造化 =====
def parse_dataframe(df: pd.DataFrame) -> List[Measurement]:
    print(f"[DEBUG] Parsing DataFrame with {len(df)} rows")
    parsed = [
        Measurement(row[0], row[1], row[2], row[3])
        for row in df.itertuples(index=False)
        if len(row) >= 4
    ]
    print(f"[DEBUG] Parsed {len(parsed)} Measurement entries")
    return parsed

def load_vehicle_data(data_dir: str, config: Dict) -> ParsedData:
    parsed = ParsedData()

    for module_name, module_cfg in config.get('modules', {}).items():
        module_file = module_cfg.get('file')
        if not module_file:
            continue
        path = os.path.join(data_dir, module_file)
        df = load_csv(path)
        if df.empty:
            continue
        all_data = parse_dataframe(df)

        # 必要なIDだけフィルタリング
        target_ids = {item['id'] for item in module_cfg.get('items', [])}
        filtered = [m for m in all_data if m.group in target_ids]
        parsed.blockmap_by_module[module_name] = filtered

    return parsed


# ===== コメント生成（AI接続は後で実装） =====
def generate_comment(parsed: ParsedData, intent: str) -> str:
    return f"[COMMENT_PLACEHOLDER for intent={intent}]"

# ===== Markdownレポート生成 =====
def generate_markdown_report(parsed: ParsedData, config: Dict, comment: str) -> str:
    lines = ["# VCDS 車両診断レポート\n"]
    lines.append("## ブロックマップ\n")

    for module_name, measurements in parsed.blockmap_by_module.items():
        module_title = config["modules"].get(module_name, {}).get("file", module_name)
        lines.append(f"### {module_title}")
        for m in measurements:
            lines.append(f"- {m.description}: {m.actual} {m.unit}")

    lines.append("\n## アダプテーション\n（未対応）")
    lines.append("\n## コメント\n")
    lines.append(comment)
    return "\n".join(lines)


# ===== Markdown -> PDF変換 =====
def convert_markdown_to_pdf(markdown_path: str, output_pdf_path: str, wkhtmltopdf_path: Optional[str] = None):
    with open(markdown_path, 'r', encoding='utf-8') as f:
        md_text = f.read()
    html = markdown.markdown(md_text, extensions=['tables', 'fenced_code'])

    config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path) if wkhtmltopdf_path else None
    pdfkit.from_string(html, str(output_pdf_path), configuration=config)

# ===== Markdown書き込み =====
def write_report_to_file(markdown_text: str, output_path: str):
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_text)

# ===== 実行例（テスト用） =====
if __name__ == '__main__':
    config_path = './config/config_golf7_cs.yaml'
    data_dir = Path('./data')
    output_dir = Path('./output')
    output_dir.mkdir(exist_ok=True)

    config = load_config(config_path)
    print(f"[DEBUG] Loaded config keys: {list(config.keys())}")

    parsed_data = load_vehicle_data(data_dir, config)
    comment = generate_comment(parsed_data, intent='sports')
    markdown_text = generate_markdown_report(parsed_data, config, comment)

    output_md_path = output_dir / 'report.md'
    output_pdf_path = output_dir / 'report.pdf'
    write_report_to_file(markdown_text, output_md_path)

    # wkhtmltopdfのパスが必要な場合は指定（例: Windows）
    wkhtmltopdf_path = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    convert_markdown_to_pdf(output_md_path, output_pdf_path, wkhtmltopdf_path)

    print(f"✅ レポート作成完了: {output_pdf_path}")
