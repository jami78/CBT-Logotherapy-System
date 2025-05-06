
import yaml
from app.llm.llm_services import gpt
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from app.llm.agents.state import AgentState
from pydantic import BaseModel

class TransitionSignal(BaseModel):
    transition_ready: bool

class CBTAgent:
    def __init__(self):
        self.model = gpt
        self.prompt = self.get_prompt("CBT_AGENT_PROMPT")
        self.transition_prompt = self.get_prompt("CBT_TRANSITION_PROMPT")
        self.transition_model = gpt.with_structured_output(TransitionSignal)
        self.adolescent_prompt = self.get_prompt("ADOLESCENT_CBT_PROMPT")
        self.young_adult_prompt = self.get_prompt("YOUNG_ADULT_CBT_PROMPT")
        self.adult_prompt = self.get_prompt("ADULT_CBT_PROMPT")

    def get_prompt(self, name):
        with open("app/prompts/prompt.yml", "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)
            return config[name]["prompt"]
        
    def cbt_reflection_node(self, state: AgentState) -> AgentState:
        age_group = state["age_group"]
        
        if age_group == "Adolescents (10-18)":
            age_group_prompt = self.adolescent_prompt
        elif age_group == "Young Adults (19-30)":
            age_group_prompt = self.young_adult_prompt
        elif age_group == "Adults (31+)":
            age_group_prompt = self.adult_prompt
        else:
            age_group_prompt = self.young_adult_prompt

        messages = [SystemMessage(content=self.prompt.format(age_prompt= age_group_prompt))]

        for i,message in enumerate(state["messages"]):
            print(message)
            if i%2==0:
                messages.append(HumanMessage(content= message))
            else:
                messages.append(AIMessage(content=message))
        response = self.model.invoke(messages)
        transition_query = self.transition_prompt.format(feedback=response.content)
        transition_model= self.model.with_structured_output(TransitionSignal)
        transition_response = transition_model.invoke([HumanMessage(content=state["messages"][-1]), SystemMessage(content=transition_query)])
        transition_ready= transition_response.transition_ready
        return {"response": response.content, "transition_ready": transition_ready}


cbt_agent = CBTAgent()
