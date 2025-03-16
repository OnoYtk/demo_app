"""設定ファイル"""
import os
from pathlib import Path

# データベース接続設定
DB_HOST = 'localhost'
DB_PORT = os.getenv('POSTGRES_PORT', '5432')
DB_URL = f"postgresql+psycopg://demo:demo1234@{DB_HOST}:{DB_PORT}/company_survey"

# ディレクトリパス
CWD = Path(__file__).parent.parent
KNOWLEDGE_DIR = CWD.joinpath("knowledge")
OUTPUT_DIR = CWD.joinpath("output")

# 出力ディレクトリが存在しない場合は作成
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)