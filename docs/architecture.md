# TradingAgents Architecture

This document gives a fast, code-aligned view of how TradingAgents is wired together.

Core implementation anchors:

- `tradingagents/graph/trading_graph.py`
- `tradingagents/graph/setup.py`
- `tradingagents/dataflows/interface.py`

## System Architecture

```mermaid
flowchart TB
    U["User"] --> CLI["CLI / cli/main.py"]
    CLI --> CFG["DEFAULT_CONFIG + user selections"]
    CFG --> TG["TradingAgentsGraph"]
    TG --> LLM["create_llm_client()"]
    TG --> MEM["FinancialSituationMemory x5"]
    TG --> GS["GraphSetup.setup_graph()"]
    TG --> SP["SignalProcessor"]
    TG --> LOG["State Logging"]

    subgraph WF["LangGraph Workflow"]
        A1["Market Analyst"]
        A2["Social Analyst"]
        A3["News Analyst"]
        A4["Fundamentals Analyst"]
        R1["Bull Researcher"]
        R2["Bear Researcher"]
        RM["Research Manager"]
        TR["Trader"]
        K1["Aggressive Analyst"]
        K2["Conservative Analyst"]
        K3["Neutral Analyst"]
        PM["Portfolio Manager"]
    end

    GS --> WF

    A1 --> TM["tools_market"]
    A2 --> TS["tools_social"]
    A3 --> TN["tools_news"]
    A4 --> TF["tools_fundamentals"]

    subgraph TOOLS["Tool Layer"]
        T1["get_stock_data"]
        T2["get_indicators"]
        T3["get_news"]
        T4["get_global_news"]
        T5["get_insider_transactions"]
        T6["get_fundamentals"]
        T7["get_balance_sheet"]
        T8["get_cashflow"]
        T9["get_income_statement"]
    end

    TM --> TOOLS
    TS --> TOOLS
    TN --> TOOLS
    TF --> TOOLS

    TOOLS --> ROUTER["route_to_vendor() / dataflows.interface"]
    ROUTER --> YF["yfinance"]
    ROUTER --> AV["alpha_vantage"]

    A1 --> R1
    A2 --> R1
    A3 --> R1
    A4 --> R1
    R1 <--> R2
    R1 --> RM
    R2 --> RM
    RM --> TR
    TR --> K1
    K1 <--> K2
    K2 <--> K3
    K3 --> PM
    PM --> DEC["final_trade_decision"]
    DEC --> SP
    SP --> RATE["BUY / OVERWEIGHT / HOLD / UNDERWEIGHT / SELL"]

    CLI --> OUT1["results/.../reports/complete_report.md"]
    CLI --> OUT2["results/.../message_tool.log"]
    LOG --> OUT3["results/.../logs/full_states_log_*.json"]
```

## Execution Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant C as CLI
    participant G as TradingAgentsGraph
    participant LG as LangGraph
    participant AN as Analyst Team
    participant RS as Research Team
    participant TR as Trader
    participant RK as Risk Team
    participant PM as Portfolio Manager
    participant SP as SignalProcessor
    participant FS as Filesystem

    U->>C: Input ticker / date / provider / depth
    C->>C: Build config and selected analysts
    C->>G: Initialize TradingAgentsGraph(config)
    G->>G: Create LLM clients, memories, tool nodes, graph
    C->>LG: graph.stream(initial_state)

    loop Analysts run in sequence
        LG->>AN: Execute analyst node
        alt Tool call needed
            AN->>LG: Emit tool_calls
            LG->>AN: Return vendor-backed tool results
        end
        AN->>LG: Persist report into state
    end

    loop Bull/Bear debate
        LG->>RS: Bull Researcher
        RS->>LG: Bull argument
        LG->>RS: Bear Researcher
        RS->>LG: Bear argument
    end

    LG->>RS: Research Manager
    RS->>LG: investment_plan

    LG->>TR: Trader
    TR->>LG: trader_investment_plan

    loop Risk debate
        LG->>RK: Aggressive Analyst
        RK->>LG: Aggressive response
        LG->>RK: Conservative Analyst
        RK->>LG: Conservative response
        LG->>RK: Neutral Analyst
        RK->>LG: Neutral response
    end

    LG->>PM: Portfolio Manager
    PM->>LG: final_trade_decision

    LG->>G: Return final_state
    G->>SP: process_signal(final_trade_decision)
    SP-->>G: Rating only

    G->>FS: Write state log JSON
    C->>FS: Write reports and message/tool log
    C-->>U: Show final report and rating
```
