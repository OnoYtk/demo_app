"""SQLエージェントの実装"""
from pathlib import Path
from textwrap import dedent
from typing import Optional
import os

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.file import FileTools
from agno.tools.sql import SQLTools
from agno.storage.agent.postgres import PostgresAgentStorage
from agno.knowledge.combined import CombinedKnowledgeBase
from agno.knowledge.json import JSONKnowledgeBase
from agno.knowledge.text import TextKnowledgeBase
from agno.vectordb.pgvector import PgVector
from agno.embedder.openai import OpenAIEmbedder

from .config import DB_URL, OUTPUT_DIR, KNOWLEDGE_DIR

def load_prompt(filename: str) -> str:
    """プロンプトをマークダウンファイルから読み込む"""
    prompt_dir = Path(__file__).parent / "prompts"
    prompt_path = prompt_dir / f"{filename}.md"
    return prompt_path.read_text(encoding="utf-8")

def get_sql_agent(
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    debug_mode: bool = True,
) -> Agent:
    """SQLエージェントのインスタンスを返す"""
    # モデルを作成
    model = OpenAIChat(id="gpt-4o")
    
    # ストレージを設定
    agent_storage = PostgresAgentStorage(
        db_url=DB_URL,
        table_name="survey_agent_sessions",
        schema="public",
    )
    
    # ナレッジベースを設定
    agent_knowledge = CombinedKnowledgeBase(
        sources=[
            TextKnowledgeBase(
                path=KNOWLEDGE_DIR,
                formats=[".txt", ".sql", ".md"],
            ),
            JSONKnowledgeBase(path=KNOWLEDGE_DIR),
        ],
        vector_db=PgVector(
            db_url=DB_URL,
            table_name="survey_agent_knowledge",
            schema="public",
            embedder=OpenAIEmbedder(id="text-embedding-3-small"),
        ),
        num_documents=5,
    )
    
    # プロンプトの読み込み
    description = load_prompt("description")
    instructions = load_prompt("instructions")
    rules = load_prompt("rules")
    
    return Agent(
        name="Survey SQL Agent",
        model=model,
        user_id=user_id,
        session_id=session_id,
        storage=agent_storage,
        knowledge=agent_knowledge,
        search_knowledge=True,
        read_chat_history=True,
        read_tool_call_history=True,
        tools=[SQLTools(db_url=DB_URL), FileTools(base_dir=OUTPUT_DIR)],
        add_history_to_messages=True,
        num_history_responses=3,
        debug_mode=debug_mode,
        description=dedent(description),
        instructions=dedent(f"""\
        {instructions}
        以下のルールを必ず守ってください：
        <rules>
        {rules}
        </rules>\
        """),
    )