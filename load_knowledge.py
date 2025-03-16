"""ナレッジベースを読み込む"""
from agents.agent import get_sql_agent
from agno.utils.log import logger

def load_knowledge(recreate: bool = True):
    """ナレッジベースをロード"""
    logger.info("Loading knowledge base...")
    
    # エージェントを一時的に作成してナレッジベースを読み込む
    agent = get_sql_agent()
    agent.knowledge.load(recreate=recreate)
    
    logger.info("Knowledge base loaded successfully")

if __name__ == "__main__":
    load_knowledge()