"""Streamlitアプリケーション"""
import streamlit as st
from agents import get_sql_agent
from agno.agent import Agent
from utils import (
    CUSTOM_CSS,
    add_message,
    display_tool_calls,
    restart_agent,
)

# ページ設定
st.set_page_config(
    page_title="社員アンケート分析",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# カスタムCSSの適用
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

def main() -> None:
    # ヘッダー
    st.markdown("<h1 class='main-title'>社員アンケート分析アシスタント</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='subtitle'>社員の声を分析し、インサイトを提供します</p>",
        unsafe_allow_html=True,
    )
    
    # エージェントの初期化
    sql_agent: Agent
    if "survey_agent" not in st.session_state or st.session_state["survey_agent"] is None:
        sql_agent = get_sql_agent()
        st.session_state["survey_agent"] = sql_agent
    else:
        sql_agent = st.session_state["survey_agent"]
    
    # エージェントセッションの読み込み
    try:
        st.session_state["survey_agent_session_id"] = sql_agent.load_session()
    except Exception:
        st.warning("エージェントセッションを作成できませんでした。データベースは起動していますか？")
        return
    
    # 実行履歴の読み込み
    agent_runs = sql_agent.memory.runs
    if len(agent_runs) > 0:
        st.session_state["messages"] = []
        for _run in agent_runs:
            if _run.message is not None:
                add_message(_run.message.role, _run.message.content)
            if _run.response is not None:
                add_message("assistant", _run.response.content, _run.response.tools)
    else:
        st.session_state["messages"] = []
    
    # サイドバー
    with st.sidebar:
        st.markdown("#### 📊 サンプル質問")
        
        if st.button("👥 部署別のポジティブなコメント数"):
            add_message("user", "部署ごとのポジティブなコメント数を教えてください")
        
        # if st.button("🔍 「改善」を含むコメント"):
        #     add_message("user", "「改善」という単語を含むコメントを検索してください")
        
        if st.button("📊 性別と部署ごとのコメント数"):
            add_message("user", "性別と部署ごとのコメント数を集計してください")
        
        st.markdown("#### 🛠️ ユーティリティ")
        if st.button("🔄 新規チャット"):
            restart_agent()
    
    # ユーザー入力
    if prompt := st.chat_input("👋 社員アンケートについて質問してください"):
        add_message("user", prompt)
    
    # チャット履歴の表示
    for message in st.session_state["messages"]:
        if message["role"] in ["user", "assistant"]:
            _content = message["content"]
            if _content is not None:
                with st.chat_message(message["role"]):
                    # ツール呼び出しがあれば表示
                    if "tool_calls" in message and message["tool_calls"]:
                        display_tool_calls(st.empty(), message["tool_calls"])
                    st.markdown(_content)
    
    # ユーザーメッセージへの応答生成
    last_message = (
        st.session_state["messages"][-1] if st.session_state["messages"] else None
    )
    if last_message and last_message.get("role") == "user":
        question = last_message["content"]
        with st.chat_message("assistant"):
            # ツール呼び出し用コンテナ
            tool_calls_container = st.empty()
            resp_container = st.empty()
            
            with st.spinner("🤔 考え中..."):
                response = ""
                try:
                    # エージェントを実行して応答をストリーミング
                    run_response = sql_agent.run(question, stream=True)
                    for _resp_chunk in run_response:
                        # ツール呼び出しがあれば表示
                        if _resp_chunk.tools and len(_resp_chunk.tools) > 0:
                            display_tool_calls(tool_calls_container, _resp_chunk.tools)
                        # 応答を表示
                        if _resp_chunk.content is not None:
                            response += _resp_chunk.content
                            resp_container.markdown(response)
                    
                    add_message("assistant", response, sql_agent.run_response.tools)
                
                except Exception as e:
                    error_message = f"申し訳ありません、エラーが発生しました: {str(e)}"
                    add_message("assistant", error_message)
                    st.error(error_message)

if __name__ == "__main__":
    main()