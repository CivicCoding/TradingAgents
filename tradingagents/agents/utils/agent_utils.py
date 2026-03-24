from langchain_core.messages import HumanMessage, RemoveMessage

# Import tools from separate utility files
from tradingagents.agents.utils.core_stock_tools import (
    get_stock_data
)
from tradingagents.agents.utils.technical_indicators_tools import (
    get_indicators
)
from tradingagents.agents.utils.fundamental_data_tools import (
    get_fundamentals,
    get_balance_sheet,
    get_cashflow,
    get_income_statement
)
from tradingagents.agents.utils.news_data_tools import (
    get_news,
    get_insider_transactions,
    get_global_news
)


def build_instrument_context(ticker: str) -> str:
    """Describe the exact instrument so agents preserve exchange-qualified tickers."""
    return (
        f"The instrument to analyze is `{ticker}`. "
        "Use this exact ticker in every tool call, report, and recommendation, "
        "preserving any exchange suffix (e.g. `.TO`, `.L`, `.HK`, `.T`)."
    )


def build_chinese_output_instruction(extra_requirements: str = "") -> str:
    """Return a shared instruction for Chinese-language model output.

    Keeps internal control tokens in English so existing graph logic still works.
    """
    base_instruction = (
        "Write all natural-language analysis, explanations, and report content in Simplified Chinese. "
        "Keep stock tickers, tool names, and exact technical indicator names unchanged. "
        "If you must output a formal rating or control token required by the workflow, keep that rating token in English exactly as requested. "
        "Do not switch back to English for normal narrative text."
    )

    if extra_requirements:
        return f"{base_instruction} {extra_requirements}"

    return base_instruction

def create_msg_delete():
    def delete_messages(state):
        """Clear messages and add placeholder for Anthropic compatibility"""
        messages = state["messages"]

        # Remove all messages
        removal_operations = [RemoveMessage(id=m.id) for m in messages]

        # Add a minimal placeholder message
        placeholder = HumanMessage(content="Continue")

        return {"messages": removal_operations + [placeholder]}

    return delete_messages


        
