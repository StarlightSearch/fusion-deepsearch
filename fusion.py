from typing import List, Optional
from pydantic import BaseModel
from google import genai
from store import VectorStore 
from exa_py import Exa
import os
import gradio as gr
import argparse

def get_rephraser_prompt(
    question: str,
    local_observations: Optional[List[str]] = [],
    web_observations: Optional[List[str]] = [],
    previous_queries: Optional[List[str]] = [],
) -> str:
    if len(local_observations)==0 and len(web_observations)==0:
        template = f"""You are an assistant tasked with taking a natural languge query from a user
and converting it into a query for a vectorstore. These queries are used to do deep research on a topic provided. In the process, strip out all 
information that is not relevant for the retrieval task and return a new, simplified
question for vectorstore retrieval. Always provide the respone in the given JSON format

Write the queries such that it explores different perspectives of the of topics related to the user query. Give 3 different queries.
Here is the user query: {question}

Set the done flag to False
"""
    else:
        local_observations = "\n".join(local_observations)            
        if len(web_observations) > 0:
            web_observations = "\n".join(web_observations)
            template = f"""You are an assistant tasked with taking a natural languge query from a user
and converting it into a query for a vectorstore. In the process, strip out all 
information that is not relevant for the retrieval task and return a new, simplified
question for vectorstore retrieval. 


The following information is already collected. The information within the <local_observation> tag is collected from the local documents that the user has. The infomation withing the <web_observations> tag is collected from the web. 
The previously used queries are also provided within the <previous_queries> tag. Make sure to provide more queries that explore different perspectives of the topic.  

You should give more focus on the local observations and use the web observations only if needed. 

<previous_queries>
{previous_queries}
</previous_queries>

<local_observations>
{local_observations}
</local_observations>

<web observations>
{web_observations}
</web_observations>


Based on this observations, you have two options:
1. Find knowledge gaps that still need to be explored and write 3 different queries that explore different perspectives of the topic. If this is the case set the done flag to False.
2. If there are no more knowledge gaps and you have enough information related to the topic, you dont have to provide any more queries and you can set the done flag to True. 

Before setting the done flag to true, make sure that the following conditions are met: 
1. You have explored different perspectives of the topic
2. You have collected some opposing views
3. You have collected some supporting views
4. You have collected some views that are not directly related to the topic but can be used to explore the topic further.

Here is the user query that the user wants to do deep research on.
User query: {question}

Always provide the respone in the given JSON format

    """
        else:
            template = f"""You are an assistant tasked with taking a natural languge query from a user
and converting it into a query for a vectorstore. In the process, strip out all 
information that is not relevant for the retrieval task and return a new, simplified
question for vectorstore retrieval. 


The following information is already collected. The information within the <local_observation> tag is collected from the local documents that the user has.
The previously used queries are also provided within the <previous_queries> tag. Make sure to provide more queries that explore different perspectives of the topic.  

<previous_queries>
{previous_queries}
</previous_queries>

<local_observations>
{local_observations}
</local_observations>


Based on this observations, you have two options:
1. Find knowledge gaps that still need to be explored and write 3 different queries that explore different perspectives of the topic. If this is the case set the done flag to False.
2. If there are no more knowledge gaps and you have enough information related to the topic, you dont have to provide any more queries and you can set the done flag to True. 

Before setting the done flag to true, make sure that the following conditions are met: 
1. You have explored different perspectives of the topic
2. You have collected some opposing views
3. You have collected some supporting views
4. You have collected some views that are not directly related to the topic but can be used to explore the topic further.

Here is the user query that the user wants to do deep research on.
User query: {question}

Always provide the respone in the given JSON format

    """
    return template

client = genai.Client()

if os.path.exists("doc"):
    my_store =  VectorStore("doc")
else:
    os.mkdir("doc")
    my_store =  VectorStore("doc")
exa = Exa(api_key=os.environ.get("EXA_API_KEY"))

web_search  = False

class QueryRephase(BaseModel):
    content: str
    querys: list[str]
    done: bool

question = "How are transformer models trained?"


def rephrase(prompt: str) -> list:
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=prompt,
        config={
            'response_mime_type': 'application/json',
            'response_schema': QueryRephase,
        },
    )
    return response.text

def query_response(prompt: str) -> QueryRephase:
    response = rephrase(prompt)
    my_recipes= str(response)
    out = QueryRephase.model_validate_json(my_recipes)
    return out

def report_response(prompt: str) -> str:
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=prompt,
    )
    return response.text

def get_observations(queries: List[str]) -> List[str]:
    local_observations = []
    web_observations = []
    for query in queries:
        local_observation = my_store.forward(query)
        local_observation = [f"Question: {query}"] + local_observation
        local_observations.extend(list(local_observation))

        if web_search:
            web_result = exa.search_and_contents(
                query, type="auto", text=True, num_results=3
            )
            web_observation = []
            for result in web_result.results:
                observation = f"Title: {result.title} \n URL: {result.url} \n Content: {result.text}"
                web_observation.append(observation)
            web_observation = [f"Question: {query}"] + web_observation
            web_observations.extend(web_observation)

    return local_observations, web_observations


def do_research(question: str, max_steps: int = 5) -> List[str]:
    local_observations, web_observations, previous_queries = [], [], []
    for i in range(max_steps):
        print("Step Number: ", i)
        prompt = get_rephraser_prompt(question, local_observations, web_observations, previous_queries)
        query_responses = query_response(prompt)
        print("Searching with queries: ", "\n".join(query_responses.querys))
        print("Done: ", query_responses.done)
        if query_responses.done:
            break
        local_observation, web_observation= get_observations(query_responses.querys)
        if len(local_observations)==0 and len(web_observations)==0:
            local_observations = local_observation
            web_observations = web_observation
        else:
            local_observations.extend(local_observation)
            web_observations.extend(web_observation)
    return local_observations, web_observations

local_observations, web_observations = do_research(question)


def write_report(question: str, local_observations: List[str], web_observations: List[str]) -> None:
    if len(web_observations) > 0:
        template = f"""You are an expert in writing reports. You are provided with the user query and the collected information from both local and web sources. 
The local information is within the <local_observations> tag and the web information is within the <web_observations> tag.

<local_observations>
{local_observations}
</local_observations>

<web_observations>
{web_observations}
</web_observations>

Write a detailed report on the user query based on the information provided. You should provide a detailed analysis of the topic and provide a summary of the information collected from both local and web sources

Instructions:
1. Write a detailed report on the user query based on the information provided. You should provide a detailed analysis of the topic and provide a summary of the information collected from both local and web sources
2. Format the report in a way that is easy to read and understand
3. Do not explicitly mention if the output is from local or web observations. Just write the report as if you have all the information available.
4. Structure the report with an introduction, body and conclusion
5. Provide inline citations if needed. Cite the file name for the local observations and the URL for the web observations. Provide all references at the end of the report.
6. Provide tables if needed to show differences

Here is the user query that the user wants to do deep research on.
User query: {question}
"""

    if len(web_observations) == 0:
        template = f"""You are an expert in writing reports. You are provided with the user query and the collected information from local sources. 
The local information is within the <local_observations> tag.


<local_observations>
{local_observations}
</local_observations>

Instructions:
1. Write a detailed report on the user query based on the information provided. You should provide a detailed analysis of the topic and provide a summary of the information collected from both local and web sources
2. Format the report in a way that is easy to read and understand
3. Do not explicitly mention if the output is from local or web observations. Just write the report as if you have all the information available.
4. Structure the report with an introduction, body and conclusion
5. Provide inline citations if needed. Cite the file name. Provide all references as file name at the end of the report.
6. Provide tables if needed to show differences

Here is the user query that the user wants to do deep research on.
User query: {question}
        """

    response = report_response(template)
    return response

report = write_report(question, local_observations, web_observations)

with open("report.md", "w", encoding="utf-8") as f:
    f.write(report)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a research report based on a query.")
    parser.add_argument("question", type=str, help="The question to research.")
    parser.add_argument("--max_steps", type=int, default=5, help="Maximum number of research steps.")
    args = parser.parse_args()

    local_observations, web_observations = do_research(args.question, args.max_steps)
    report = write_report(args.question, local_observations, web_observations)
    print(report)










# def gradio_interface(question: str, max_steps: int = 5):
#     local_observations, web_observations = do_research(question, max_steps)
#     report = write_report(question, local_observations, web_observations)
#     yield report

# iface = gr.Interface(
#     fn=gradio_interface,
#     inputs=[
#         gr.Textbox(lines=2, placeholder="Enter your question here..."),
#         gr.Slider(minimum=1, maximum=10, value=5, label="Max Steps")
#     ],
#     outputs="markdown",
#     title="Deep Research Assistant",
#     description="Enter a question to get a detailed research report based on local and web observations.",
#     live=True  # Enable streaming of the output
# )

# iface.launch()
