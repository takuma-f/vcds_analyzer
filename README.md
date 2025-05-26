# VCDS ログ解析・レポート生成ツール / VCDS Log Parser & Analyzer

## 概要 / Overview

このツールは、Volkswagen / Audi 車両の VCDS ログファイル（blockmap, adapmap, diagscan）を解析し、構造化された診断レポート（Markdown / PDF）を自動生成します。

This tool parses VCDS diagnostic logs (blockmap, adapmap, diagscan) for Volkswagen / Audi vehicles and generates structured diagnostic reports in Markdown and PDF formats.

---

## 機能 / Features

- blockmap / adapmap の CSV クレンジングと構造化  
- DiagScan ファイルの故障コード解析（複数形式に対応）  
- YAML 構成ファイルによる車種ごとの設定  
- Markdown + PDF 出力対応  
- CLI からの簡易実行  
- ローカルLLMやコメント生成の拡張にも対応可能（将来的に）

---

## ファイル構成 / File Structure

```
.
├── org/                 # 入力用CSV・DiagScanファイル保存先
├── data/                # クレンジング後CSV・解析JSON出力先
├── output/              # Markdown / PDF 出力先
├── config/              # YAML 構成ファイル保存先
├── data_cleansing.py    # データクレンジング用スクリプト
├── main.py              # データ解析・レポート生成本体スクリプト
└── config_golf7_cs.yaml # Golf MKMK7 GTI Clubsport 用設定ファイル（例）
```

---

## 使い方 / How to Use

### 1. blockmap / adapmap / diagscan のクレンジング

```bash
python data_cleansing.py csv blockmap-01-xxxxx.csv
python data_cleansing.py diagscan Log-XXXX.txt
```

- `./data/` にクレンジング済CSVと `parsed_diagscan.json` を出力

### 2. レポート生成

```bash
python main.py
```

- `config/config_golf7_cs.yaml` に基づいて Markdown / PDF レポートを生成（`./output/` に出力）

---

## 前提 / Requirements

- Python 3.9+
- 依存ライブラリ：`pandas`, `markdown`, `pdfkit`, `PyYAML`
- PDF出力には `wkhtmltopdf` のインストールが必要（PATHに追加）

---

## 今後の予定 / Roadmap

- コメント生成エンジンの統合（LLM）
- サーキット診断・中古車評価用プロファイル

---

## ライセンス / License

MITライセンス（予定）  
MIT License (planned)