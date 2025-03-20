import json
import os
from google import genai 
from google.genai.types import GenerateContentConfig, Content, Part
from typing import List
from pydantic import BaseModel
import pydantic_core

from openai import OpenAI
import embed_anything
from embed_anything import EmbedData, EmbeddingModel, TextEmbedConfig, WhichModel
import numpy as np
import store
from exa_py import Exa
from dotenv import load_dotenv
from store import VectorStore


client = genai.Client(api_key="")
exa = Exa(api_key='')
mystore =  VectorStore("doc") 


template="""You are an assistant tasked with taking a natural languge query from a user
and converting it into a query for a vectorstore. In the process, strip out all 
information that is not relevant for the retrieval task and return a new, simplified
question for vectorstore retrieval. 

Write the queries such that it explores different perspectives of the of topics related to the user query. Give 3 different queries.
Here is the user query: {question} """

question = "what is attention"

prompt = template + question

class QueryRephase(BaseModel):
    content: str
    querys: list[str]

class CallGemini(BaseModel):
    content: str
    output: str

def rephrase(prompt: str = prompt) -> list:
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=prompt,
        config={
            'response_mime_type': 'application/json',
            'response_schema': QueryRephase,
        },
    )
    return response.text


def QueryResponse(prompt: str = prompt) -> list:
    response = rephrase(prompt)
    my_recipes= str(response)
    out = QueryRephase.model_validate_json(my_recipes)
    return out
# response = rephrase(prompt)
# my_recipes= str(response)
# out = QueryRephase.model_validate_json(my_recipes)
out = QueryResponse(prompt)
all_chunks = []
all_result = []
for query in out.querys:
    doc = mystore.forward(query)
    result = exa.search_and_contents(query, type="auto", text=True)
    all_chunks.append(list(doc))
    all_result.append(result)
    


mid_prompt =  " ".join(all_chunks[0]) + " " + template + " " + question + " " + " ".join(map(str, all_result)) + " " + "Give more Weightage to results from {all_chunks} thant to result from {all_results}"
mid_out = QueryResponse(mid_prompt)

new_chunks = []
messages =[]
for query in mid_out.querys:
    response = mystore.forward(query)
    new_chunks.append(list(response))

SystemPrompt = "You are a helpful assistant helping in filling the gaps of the query. You have the context of the user query and the results from the vectorstore. Your job is to check if there is enough information and answer the question. If not, you can ask the user for more information."
final_prompt = "take the context and give me the best possible answer." + " " + question + " " + " ".join(new_chunks[0])
# messages.append(Content(role='user', parts=[Part(text=prompt)]))
# messages.append(Content(role='model', parts=[Part(text=query) for query in out.querys]))
messages.append(Content(role='user', parts=[Part(text=final_prompt)]))

response = client.models.generate_content(
    model='gemini-2.0-flash',
    config=GenerateContentConfig(system_instruction=SystemPrompt),
    contents=messages,
)

print(response.text)
