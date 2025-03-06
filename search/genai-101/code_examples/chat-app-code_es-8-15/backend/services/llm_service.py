import logging
from .inference_service import es_chat_completion

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# TODO - this should not be hardcoded
index_source_fields = {
    "restaurant_reviews": [
        "Review_semantic"
    ]
}


def init_conversation_history():
    # convo = [
    #     {
    #         "role": "user",
    #         "content": "Hi, I have questions about Notary regulations"
    #     },
    #     {
    #         "role": "assistant",
    #         "content": "Sure, I can help with that. What specific questions do you have?"
    #     },
    # ]
    convo = []

    return convo


def create_llm_prompt(question, results, conversation_history):
    """
    Create a prompt for the LLM based on the question, search results, and conversation history provided
    :param question:
    :param results:
    :param conversation_history:
    :return:
    """
    logging.info("Starting to create LLM prompt")
    context = ""
    logging.info(f"Results: {results}")
    for hit in results:
        inner_hit_path = f"{hit['_index']}.{index_source_fields.get(hit['_index'])[0]}"
        logging.info(f"hit: {hit}")

        ## For semantic_text matches, we need to extract the text from the inner_hits
        if 'inner_hits' in hit and inner_hit_path in hit['inner_hits']:
            logging.info('inner_hits found')
            restaurant_name = hit['_source']['Restaurant']
            restaurant_rating = hit['_source']['Rating']
            for inner_hit in hit['inner_hits'][inner_hit_path]['hits']['hits']:
                review = inner_hit['_source']['text']

                context += f"""
                Restaurant: {restaurant_name}
                Rating: {restaurant_rating}
                Review Chunk: {review}
                """
        else:
            source_field = index_source_fields.get(hit["_index"])[0]
            hit_context = hit["_source"][source_field]
            context += f"{hit_context}\n"

    prompt = f"""
  Instructions:

- You are a helpful and knowledgeable assistant designed to assist users in finding and recommending restaurants based on provided reviews. Your primary goal is to provide accurate, personalized, and relevant restaurant recommendations using semantically matching restaurant reviews.

Guidelines:

Audience:

Assume the user could be of any experience level. Provide recommendations that cater to a variety of preferences and tastes.
Avoid overly complex jargon. Use language that is accessible and relatable to all users, regardless of their culinary knowledge.
Response Structure:

Clarity: Provide clear and direct restaurant recommendations, highlighting key aspects such as cuisine, location, atmosphere, and unique features.
Conciseness: Keep responses concise and to the point. Use bullet points to organize information where appropriate.
Formatting: Use Markdown formatting for:
Bullet points to list restaurant features or benefits
Code blocks for any specific commands or configurations (if applicable)
Relevance: Ensure the recommendations are based on semantically matching reviews, prioritizing relevance and user preference.
Content:

Personalization: Tailor recommendations based on the user's preferences, inferred from their queries or any provided details.
Examples: Include specific examples from the reviews to justify your recommendations (e.g., "Highly rated for its authentic Italian cuisine and cozy atmosphere").
Documentation Links: Suggest additional resources or links to restaurant websites, menus, or review platforms when applicable.
Context Utilization:

Use the conversation history to provide contextually relevant answers. If a user’s question seems related to a previous question or answer, reference the relevant details from the conversation history to maintain continuity.
When referring to previous messages, ensure that restaurant names, ratings, or specific details are consistent with earlier parts of the conversation.
Tone and Style:

Maintain a friendly and approachable tone.
Encourage exploration by being enthusiastic and supportive of all user queries about restaurants.

- Answer questions truthfully and factually using only the context presented.
- If you don't know the answer, just say that you don't know, don't make up an answer.
- You must always cite the review or data where the recommendation is extracted using inline academic citation style [], using the position.
- Use markdown format for examples and citations.
- Be correct, factual, precise, and reliable.

Conversation History:
{conversation_history}

Context:
{context}

The user has a question:
{question}

Answer this question using the context provided and the conversation history. If the user's question is related to a previous question or answer, use the relevant parts of the conversation history to provide a consistent and accurate response.
If the answer is not in the context, please say "I'm unable to provide a recommendation because the information is not in the context or previously discussed." DO NOT make up an answer.

   """

    logging.info(f"Done creating LLM prompt")
    logging.info(f"Full Prompt: {prompt}")
    return prompt


def build_conversation_history(history, user_message, ai_response):
    """
    Function to build converstation history for the LLM
    Keep 2 messages from the user and 2 messages from the AI
    When the count of messages from the user and AI each is greater than 2,
     keep the last 2 messages as is
     make a call to the LLM to summarize the conversation and keep the summary

    Summary is kept in the "system" role

    structure
    [
      {"role": "system", "content": "Conversation summary:  [summary here]"},
      {"role": "user", "content": "2 messages ago"},
      {"role": "assistant", "content": "2 responses ago"},
      {"role": "user", "content": "1 message ago"},
      {"role": "assistant", "content": "1 response ago"}
    ]
    """

    logging.info("Starting to build conversation history function")
    if len(history) < 4:
        logging.info("History is less than 4 messages. Adding new messages to history")
        history.extend([
            {
                "role": "user",
                "content": user_message
            },
            {
                "role": "assistant",
                "content": ai_response
            }
        ])
        new_history = history
    else:
        logging.info("History is greater than 4 messages. Summarizing conversation")
        summary_prompt = f"""
You are a conversation summarizer specializing in restaurant recommendations, reviews, and related topics. Your task is to create a detailed and accurate summary of the conversation history, incorporating the new message provided. This summary will be used as context for future interactions, so ensure it retains all relevant details, especially the specific restaurants discussed, their ratings, and key points mentioned by the user.

Rules:
1. Summarize the entire conversation, including the provided history and the new message.
2. Prioritize the restaurants mentioned in the latest user queries and assistant responses. Maintain focus on these restaurants in subsequent interactions.
3. Ensure that restaurant names, ratings, specific food items, and any notable characteristics (e.g., speed of service, atmosphere, cuisine type) are clearly retained and highlighted in the summary.
4. Avoid introducing irrelevant details or shifting focus to restaurants not part of the immediate conversation.
5. Use a structured format optimized for AI processing, keeping relevant information at the forefront. Length may exceed 150 words if necessary to maintain context.
6. Highlight any unresolved questions or areas that may require further clarification in future interactions.

Current conversation history:
{history}

New User message:
{user_message}

New Assistant response:
{ai_response}

Provide your summary in the following format:
SUMMARY: [Detailed summary focusing on the specific restaurants discussed, their key characteristics, and any user preferences or questions.]
KEY RESTAURANTS: [List of restaurant names mentioned in the conversation, along with their ratings and any specific details relevant to the user’s queries.]
RELEVANT DETAILS: [List any specific food items, service attributes, or user preferences mentioned.]
TOPICS: [List of key topics discussed, such as speed of service, food quality, or atmosphere.]
UNRESOLVED: [Any open questions or issues that may need further attention.]
        """

        # call the LLM to summarize the conversation
        # summary = query_aws_bedrock_nonstreaming(summary_prompt)
        summary = es_chat_completion(summary_prompt)
        logging.info(f"LLM Summary of history: {summary}")

        # Build new history
        new_history = [
            {
                "role": "system",
                "content": summary
            },
            history[-2],
            history[-1],
            {
                "role": "user",
                "content": user_message
            },
            {
                "role": "assistant",
                "content": ai_response
            }
        ]

    logging.info(f"New conversation history: {new_history}")

    return new_history
