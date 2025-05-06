from langgraph.graph import StateGraph, END, START
from app.llm.agents.state import AgentState
from app.llm.agents.cbt_agent import cbt_agent
from app.llm.agents.logotherapy_agent import logotherapy_agent
from app.core.checkpointer import checkpointer




def cbt_node(state: AgentState) -> AgentState:
    print("\n[CBT_NODE] Current state keys:", state.keys())
    print("[CBT_NODE] Message count:", len(state["messages"]))
    for i, msg in enumerate(state["messages"]):
        print(f"[CBT_NODE] Message {i} ({type(msg).__name__}): {msg}")
    user_input = state['messages'][-1]
    print("[CBT_NODE] Latest user input:", user_input)
    print("[CBT_NODE] Invoking CBT agent...")
    result = cbt_agent.cbt_reflection_node(state)
    print("[CBT_NODE] Agent response:", result['response'])
    if result["transition_ready"]:
        new_message= result['response']
    else:
        new_message = result['response']
    return {
            "messages": [new_message],
            "transition": result['transition_ready']
        }


def logotherapy_node(state: AgentState) -> AgentState:
    print("\n[LOGO_NODE] Current state keys:", state.keys())
    print("[LOGO_NODE] Message count:", len(state["messages"]))
    for i, msg in enumerate(state["messages"]):
        print(f"[LOGO_NODE] Message {i} ({type(msg).__name__}): {msg}")
    user_input= state["messages"][-1]
    print("[LOGO_NODE] Latest user input:", user_input)
    print("[LOGO_NODE] Invoking LOGO agent...")
    result = logotherapy_agent.logotherapy_reflection_node(state)
    print("[LOGO_NODE] Agent response:", result['response'])
    new_message = result['response']
    return {
            "messages": [new_message]
        }


def transition_condition(state: AgentState) -> str:
    return "logotherapy_node" if state.get("transition") else END 

def start_condition(state: AgentState)-> str:
    return "logotherapy_node" if state.get("transition") else "cbt_node"



builder = StateGraph(AgentState)
builder.add_node("cbt_node", cbt_node)
builder.add_node("logotherapy_node", logotherapy_node)
builder.add_conditional_edges(START, start_condition)
builder.add_conditional_edges("cbt_node", transition_condition)
builder.add_edge("logotherapy_node", END)
checkpointer.setup()
graph = builder.compile(checkpointer=checkpointer)