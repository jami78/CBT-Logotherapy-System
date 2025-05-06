import yaml
from app.llm.llm_services import gpt
from app.llm.agents.state import AgentState

from langchain.schema import SystemMessage, HumanMessage, AIMessage

class LogotherapyAgent:
    def __init__(self):
        self.model = gpt
        self.prompt = self.get_prompt("LOGOTHERAPY_AGENT_PROMPT")

    def get_prompt(self, name):
        with open("app/prompts/prompt.yml", "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)
            return config[name]["prompt"]

    def logotherapy_reflection_node(self, state: AgentState) -> AgentState:
        #user_input = state["user_input"]
        messages= [SystemMessage(content= self.prompt)]
        for i,message in enumerate(state["messages"]):
            print(message)
            if i%2==0:
                messages.append(HumanMessage(content= message))
            else:
                messages.append(AIMessage(content=message))
        response = self.model.invoke(messages)
        return {"response": response.content}

    
logotherapy_agent = LogotherapyAgent()
