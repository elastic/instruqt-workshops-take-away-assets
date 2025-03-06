import os
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services import search_service, inference_service, llm_service
from fastapi import WebSocket, APIRouter
from elasticsearch import NotFoundError

router = APIRouter()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Set this to True to stream LLM responses back to the client
# Streaming not implemented in this version
streaming_llm = False

class SearchQuery(BaseModel):
    query: str
    context_type: str


@router.post("/search")
async def perform_search(search_query: SearchQuery):
    logging.info(f"Received query: {search_query.query}")
    try:
        prompt_context = search_service.semantic_search(search_query.query, search_query.context_type)
        llm_response = bedrock_service.query_aws_bedrock(prompt_context)
        return {"prompt": prompt_context, "llm_response": llm_response}
    except Exception as e:
        logging.error(f"Error in processing search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


class ChatMessage(BaseModel):
    message: str


@router.websocket_route("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    # Initialize the conversation history
    convo_history = llm_service.init_conversation_history()

    try:
        while True:
            # Receive the message from the client (user's question)
            data = await websocket.receive_text()
            logging.debug(f"Raw data received: {data}")

            # Parse the user's question
            chat_message = ChatMessage.parse_raw(data)
            logging.info(f"Received message: {chat_message.message}")

            # create Prompt to generate retriever
            context_unparsed = search_service.perform_es_search(
                chat_message.message,
                "elastic-labs"
            )
            logging.info(f"Context received from perform_es_search")

            # Create a prompt for the LLM
            prompt = llm_service.create_llm_prompt(
                chat_message.message,
                context_unparsed,
                convo_history
             )
            logging.info(f"Created Prompt for LLM: {prompt}")
            logging.info(f"Prompt length: {len(prompt)}")


#TODO this is a mess
            # Send the contextual data back to the UI before making LLM calls
            logging.debug(f"Sending context back to UI: {context_unparsed}")
            logging.info("building tmp_context")
            # logging.info(context_unparsed)
            # tmp_context = ('\n---------------------------------------------------------\n\n'
            #                '---------------------------------------------------------\n\n\n').join(context_unparsed)
            tmp_context = ""
            for hit in context_unparsed:
                tmp_context += f"str{hit}\n\n"

            await websocket.send_json({
                "type": "verbose_info",
                "text": f"Context gathered from Elasticsearch\n\n{tmp_context}"
                        # f"Elasticsearch\n\n---------------------------------------------------------\n\n"
                        # f"---------------------------------------------------------\n\n{tmp_context}"
            })


            # Call the LLM to generate a response
            if not streaming_llm:
                logging.info(f"sending prompt {prompt}")
                # use Elastic to call chat completion - response is full response
                response = inference_service.es_chat_completion(prompt,
                                                                # "openai_chat_completions"
                                                                os.getenv('INFERENCE_ID')
                                                                )

                logging.info(f"Response from LLM: {response}")


                logging.info(f"Sending response to client")
                await websocket.send_json({
                    "type": "full_response",
                    "text": response
                })


            # Add the user's question and the LLM response to the conversation history
            logging.info("Building conversation history")
            convo_history = llm_service.build_conversation_history(history=convo_history,
                                                                       user_message=chat_message.message,
                                                                       ai_response=response
                                                                       )
            logging.debug(f"Conversation history: {convo_history}")
            tmp_convo_hist = '\n---------------------------------------------------------\n\n'.join(
                [str(h) for h in convo_history])
            await websocket.send_json({
                "type": "verbose_info",
                "text": f"Conversation history updated:\n\n{tmp_convo_hist}"
            })

    except Exception as e:
        logging.error("WebSocket encountered an error:", exc_info=True)
        await websocket.close(code=1001)
