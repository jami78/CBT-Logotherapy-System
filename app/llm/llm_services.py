from app.core.config import get_settings
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationSummaryMemory
from langchain.chains import ConversationChain
settings = get_settings()

OPENAI_API_KEY = settings.OPENAI_API_KEY


gpt = ChatOpenAI(
    model_name="gpt-4o",
    openai_api_key=OPENAI_API_KEY,
    temperature=0.2
)
memory = ConversationSummaryMemory(llm=gpt, max_token_limit=1000)
conv= ConversationChain(llm=gpt, memory=memory, verbose=True)
