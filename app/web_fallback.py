import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()
client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def search_web(query):
    results = client.search(query=query, max_results=1)
    if results and results["results"]:
        return results["results"][0]["content"]
    return "Sorry, I couldn't find any information."
