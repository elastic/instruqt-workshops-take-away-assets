def create_prompt(question, results, index_source_fields):
    context = ""
    for hit in results:
        source_field = index_source_fields.get(hit["_index"], [""])[0]
        context += f"{hit['_source'].get(source_field, '')}\n"

    prompt = f"""
  Instructions:
  - You are an assistant for question-answering questions about rules and regulations related to being a notary...
  Context:
  {context}
  Question: {question}
  Answer:
  """
    return prompt
