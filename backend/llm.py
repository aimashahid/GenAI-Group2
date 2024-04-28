import os
from langchain_fireworks import Fireworks
from langchain.tools import DuckDuckGoSearchRun
from langchain.agents import Tool
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain.agents import initialize_agent
from gfc import fact_check_claim
import re


os.environ["FIREWORKS_API_KEY"] = "1yR1x6rnM2AfusPPmHLHGrw40xMujZZbVGj5vzGzGyx1VHAj"
os.environ["SERPER_API_KEY"] = "71dec5a8911e77cf4b02622b06f25e2d3661f1f9"




def get_response(text):
    
    llm = Fireworks(
        model="accounts/fireworks/models/llama-v3-70b-instruct",
        max_tokens=256)




    ddg_search = DuckDuckGoSearchRun()
    google_search = GoogleSerperAPIWrapper()

    tools = [
    Tool(
        name="DuckDuckGo Search",
        func=ddg_search.run,
        description="Useful to browse information from the Internet.",
    ),
        Tool(
        name="Google Search",
        func=google_search.run,
        description="Useful to search in Google. Use by default.",
    )
    ]

    agent = initialize_agent(
    tools, llm, agent="zero-shot-react-description", verbose=True
    )

    # prompt = f"Here is a statement: {text}. Make a list of assumptions you made when given the above statement and classify it as true or fake news."
    fact = fact_check_claim(text)
    print("fact ", fact)
    if fact != "":
        prompt = f"Here is a statement: {text}. We asked Google Fact Check API to verify our claim. Here's what it said: {fact}. Make a list of assumptions you made when given the above statement and classify it as true or fake news. If the news is fake, further classify it as misinformation, propaganda or misleading content as done by Google Fact Check API. Also you must assign a numerical rating to the claim on a scale of 1 to 5 where 1 means completely true and 5 means completely false."
    else:
        prompt = f"Here is a statement: {text}. Make a list of assumptions you made when given the above statement and classify it as true or fake news. If the news is fake, further classify it as misinformation, propaganda or misleading content as done by Google Fact Check API. Also assign a numerical rating to the claim on a scale of 1 to 5 where 1 means completely true and 5 means completely false."
    x = agent.invoke(prompt)
    print(x)
    
    # removing tokens
    def remove_after(text, delimiter):
        return text.split(delimiter)[0].strip()

    cleaned_data = remove_after(x['output'], '<|eot_id|>')
    
    # removing special characters
    def clean_text(text):
        text = text.replace('\\n', ' ').replace('\\', '')
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    cleaned_data = clean_text(cleaned_data)
    
    return cleaned_data
    # return x['output']
