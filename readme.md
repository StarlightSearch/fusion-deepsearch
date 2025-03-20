# Fusion DeepSearch

`fusion.py` is a powerful script designed to perform deep search with fusion of local docs built by embedanything and search through internet using EXA. It shows the power of agentic response with GEMINI.


## How to use system prompt and assign roles with Gemini


```python
SystemPrompt = "You are a helpful assistant helping in filling the gaps of the query. You have the context of the user query and the results from the vectorstore. Your job is to check if there is enough information and answer the question. If not, you can ask the user for more information."

final_prompt = "take the context and give me the best possible answer." + " " + question + " " + " ".join(new_chunks[0])

messages.append(Content(role='user', parts=[Part(text=prompt)]))
messages.append(Content(role='model', parts=[Part(text=query) for query in out.querys]))
messages.append(Content(role='user', parts=[Part(text=final_prompt)]))

response = client.models.generate_content(
    model='gemini-2.0-flash',
    config=GenerateContentConfig(system_instruction=SystemPrompt),
    contents=messages,
)
```

**will add more information soon**