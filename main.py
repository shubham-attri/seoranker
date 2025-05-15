from langchain_ollama.llms import OllamaLLM

from langchain.chat_models import init_chat_model
from ingestcontent import extract_markdown_from_url, search_google
import json

llm = init_chat_model("qwen3:1.7b", model_provider="ollama")



result = extract_markdown_from_url("https://sleepyowl.co/collections/premium-instant-coffee?srsltid=AfmBOooZE27KxJPLx64dtZ60tfBSdztGy90EAXz6msyyahzuD19zAaxw","sleepyowl.json")

response = llm.invoke([
    {"role": "user", "content": " Does the conent in the following markdown is good for SEO and which pages should we target only tell those we will skip brand pages, give direct answer as yes or no?\n\n{result}"}
])

with open("llmanswer", "w", encoding="utf-8") as f:
    f.write(response.content)



from langgraph.graph import StateGraph, END

class AgentState(dict): 
    pass

builder = StateGraph(AgentState)

# Add nodes
builder.add_node("web_extractor", extract_markdown_from_url)
builder.add_node("search_engine", search_google)

# Define edges
builder.add_edge("web_extractor", "search_engine")
builder.add_edge("search_engine", END)

# Set entry point
builder.set_entry_point("web_extractor")

# Compile graph
research_agent = builder.compile()


async def run_research(url: str):
    async for step in research_agent.astream(
        {"url": url},
        {"recursion_limit": 3}
    ):
        if "web_extractor" in step:
            print(f"Extracted {len(step['web_extractor']['h1s'])} headings")
        elif "search_engine" in step:
            print(f"Found {len(step['search_engine']['organic_results'])} results")

# Run with your URL
url = "https://www.eatingwell.com/is-instant-coffee-bad-for-you-8382772"
asyncio.run(run_research(url))

