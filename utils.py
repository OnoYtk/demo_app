"""ユーティリティ関数"""
from typing import Any, Dict, List, Optional
import streamlit as st
from agents import get_sql_agent
from agno.agent.agent import Agent

def add_message(
    role: str, content: str, tool_calls: Optional[List[Dict[str, Any]]] = None
) -> None:
    """メッセージをセッション状態に追加"""
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    
    st.session_state["messages"].append(
        {"role": role, "content": content, "tool_calls": tool_calls}
    )

def restart_agent():
    """エージェントをリセットしてチャット履歴をクリア"""
    st.session_state["survey_agent"] = None
    st.session_state["survey_agent_session_id"] = None
    st.session_state["messages"] = []
    st.rerun()

def display_tool_calls(tool_calls_container, tools):
    """ツール呼び出しの表示"""
    with tool_calls_container.container():
        for tool_call in tools:
            _tool_name = tool_call.get("tool_name")
            _tool_args = tool_call.get("tool_args")
            _content = tool_call.get("content")
            
            with st.expander(
                f"🛠️ {_tool_name.replace('_', ' ').title()}", expanded=False
            ):
                if isinstance(_tool_args, dict) and "query" in _tool_args:
                    st.code(_tool_args["query"], language="sql")
                if _content:
                    st.markdown("**結果:**")
                    try:
                        st.json(_content)
                    except Exception:
                        st.markdown(_content)

# カスタムCSS
CUSTOM_CSS = """
<style>
.main-title {
    text-align: center;
    background: linear-gradient(45deg, #3498db, #2980b9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.5em;
    font-weight: bold;
    padding: 0.8em 0;
}
.subtitle {
    text-align: center;
    color: #666;
    margin-bottom: 2em;
}
.stButton button {
    width: 100%;
    border-radius: 10px;
    margin: 0.2em 0;
}
</style>
"""