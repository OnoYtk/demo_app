import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path
from agents.config import DB_URL
from agno.utils.log import logger


def create_schema():
    """スキーマとテーブルを作成"""
    engine = create_engine(DB_URL)
    with engine.connect() as conn:
        # データベースの準備（存在しない場合のみテーブルを作成）
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS employee_survey (
            question_id INTEGER,
            comment TEXT,
            department VARCHAR(50),
            gender VARCHAR(10),
            join_year INTEGER,
            sentimental VARCHAR(20)
        );
        """))
        conn.commit()
        print("テーブルの作成が完了しました")

def load_survey_data(csv_file_path):
    """CSVファイルからデータを読み込み、データベースに保存する"""
    
    print(f"CSVファイル {csv_file_path} をデータベースに読み込んでいます...")
    
    # CSVファイルを読み込む
    df = pd.read_csv(csv_file_path)
    
    # データのバリデーション
    # question_idが指定された値のいずれかであることを確認
    valid_question_ids = ["4", "16", "29", "49", "59"]
    df = df[df['question_id'].astype(str).isin(valid_question_ids)]
    
    # departmentが指定された値のいずれかであることを確認
    valid_departments = ["人事部", "営業部", "研究開発部", "マーケティング部"]
    df = df[df['department'].isin(valid_departments)]
    
    # genderが指定された値のいずれかであることを確認
    valid_genders = ["男", "女"]
    df = df[df['gender'].isin(valid_genders)]
    
    # join_yearが指定された値のいずれかであることを確認
    valid_join_years = ["2020", "2021", "2022", "2023"]
    df = df[df['join_year'].astype(str).isin(valid_join_years)]
    
    # sentimentalが指定された値のいずれかであることを確認
    valid_sentimentals = ["Neutral", "Negate", "Positive"]
    df = df[df['sentimental_by_gemini'].isin(valid_sentimentals)]
    
    # 列名を変更（sentimental_by_gemini → sentimental）
    df = df.rename(columns={'sentimental_by_gemini': 'sentimental'})
    
    # SQLAlchemyエンジンを作成
    engine = create_engine(DB_URL)
    
    # DataFrameをSQLテーブルに変換
    df.to_sql('employee_survey', engine, if_exists='replace', index=False)
    
    print(f"データベースへの読み込みが完了しました。{len(df)}行のデータがロードされました。")
    
if __name__ == "__main__":
    
    # データディレクトリの確認
    data_dir = Path("csv_data")
    # CSVファイルのパス
    csv_path = data_dir / "freee_comments_ad_department_filtered_with_sentimental_by_gemini_cleaned.csv"
    
    # CSVファイルが存在しない場合のサンプル作成
    if not csv_path.exists():
        print("サンプルCSVファイルが見つかりません。")
        # ダユーザーにパスを確認する
        user_path = input("CSVファイルの絶対パスを入力してください: ")
        if user_path:
            csv_path = Path(user_path)
    
    # スキーマの作成
    create_schema()
    
    # データのロード
    load_survey_data(csv_path)