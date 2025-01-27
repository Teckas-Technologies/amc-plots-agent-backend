from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.llms.openai import OpenAI
from llama_index.llms.openai.base import ChatMessage

# from llama_index.readers.file import PandasCSVReader
from llama_index.core import SummaryIndex
from llama_index.readers.mongodb import SimpleMongoReader

import pymongo

import os
import openai
import json
from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY') # load OPENAI_API_KEY using .env file

# MongoDB connection URL
mongo_url = os.getenv("MONGO_URL")

# Create MongoDB client using pymongo
client = pymongo.MongoClient(mongo_url)

# Extract database and collection name
db_name = "test"  # Replace with your actual database name
collection_name = "amc_agent_plots"  # Replace with your actual collection name

# Use the MongoDB client to access the desired collection
db = client[db_name]
collection = db[collection_name]

# Query dictionary for retrieving documents (you can adjust this to your needs)
query_dict = {}

# Specify the fields to retrieve (e.g., "text" field)
field_names = [ "zone", "ward", "tpNo", "fpNo", "Status", "Purpose", "Area", "address", "possesionYN", "PossessionArea", "nameOfDept", "Use", "residentUnit", "residentArea", "commercialUnit", "commercialArea", "industrialUnit", "industrialArea", "otherUnits", "otherArea", "totalUnit", "totalArea", "entryNo", "Date", "compWallYN", "compWallNo", "infoEngg", "ownershipInstalled", "wellDeveloped", "Court", "year", "caseStatus", "openOrNot", "USE", "dateOfAllot", "situation", "publicPurpose" ]
# field_names = ["arttitle", "campaignId", "colouredArt"]

# Initialize the reader
reader = SimpleMongoReader(uri=mongo_url)  # Use the full URL, no need for separate host/port

# Load data using SimpleMongoReader
documents = reader.load_data(db_name, collection_name, field_names, query_dict=query_dict)

# print("Retrieved Documents:")
# for doc in documents:
#     print(doc)

# Create the index
index = SummaryIndex.from_documents(documents)

# Load custom data from data directory to the vector store storage directory
# data = SimpleDirectoryReader(input_dir="csv_data").load_data()  # "data"
# index = VectorStoreIndex.from_documents(data)
# index.storage_context.persist()

# memory variable to store limited chat history.
memory = ChatMemoryBuffer.from_defaults(token_limit=8192)

# Read custom data from storage directory
# storage_context = StorageContext.from_defaults(persist_dir="storage")
# index = load_index_from_storage(storage_context=storage_context)

# chat engine configurations
llm = OpenAI(model="gpt-4o", temperature=0.1)

chat_engine = index.as_chat_engine(
    chat_mode="condense_plus_context",
    llm=llm,
    verbose=False,
    system_prompt=(
        """
            Prompt:-
            Your name is Leasa. You are an Artificial Intelligence Life Assistant, specialising in normal interactions, friendly talk, natural conversation, and managing questions related to the "Ahmedabad Municipal Corporation". You are also responsible for handling questions about the "amc_agent_plots" collection in MongoDB. All your responses must be structured as JSON objects with specified fields.
            Capabilities:
            You are expert in :
                - Current events
                - Historical facts
                - Science and technology
                - Arts and entertainment
                - Personal interests and hobbies
                - Travel and adventure
                - Food and cuisine
                - Lifestyle and health
                - and much more!

            MongoDB Collection Details:
                - Collection: amc_agent_plots
                - Fields: "sNo", "zone", "ward", "tpNo", "fpNo", "Status", "Purpose", "Area", "address", "possesionYN", "PossessionArea", "nameOfDept", "Use", "residentUnit", "residentArea", "commercialUnit", "commercialArea", "industrialUnit", "industrialArea", "otherUnits", "otherArea", "totalUnit", "totalArea", "entryNo", "Date", "compWallYN", "compWallNo", "infoEngg", "ownershipInstalled", "wellDeveloped", "Court", "year", "caseStatus", "openOrNot", "USE", "dateOfAllot", "situation", "publicPurpose"

            User can also want to know the plot details by the serial number (sNo).

            JSON Response Structure:
            Your JSON response must include:
            {
                "intent": "Describe the user's query in one or two words",
                "response": "Response message for the user's query in markdown or tabular",
            }
            Instructions for Handling Inputs:
            You don't learn anything from the user query.
            If you respond with list of data then the response must in tabular format.
            Name Handling:
            If the user calls your name with a small mistake, you don't need to correct it. However, if the user completely misspells your name, you must state with your correct name with the JSON format.
            Note: All responses must strictly be in JSON format.
            """
    ),
)

# Function - To generate token response
# Params - query contains user's query
# return data object response
def generate_chat_responses(user_id, query):

    history = memory.chat_store.get_messages(key=user_id)

    if history is not None:
        chat_history_converted = [ChatMessage(role=message['role'], content=str(message['content'])) for message in history]
        response = chat_engine.chat(query, chat_history=chat_history_converted)
    else:
        response = chat_engine.chat(query)

    memory.chat_store.add_message(key=user_id, message={"role": "assistant", "content": response})

    str_response = str(response)

    print(str_response)

    if str_response.startswith("```json") and str_response.endswith("```"):
        cleaned_response = str_response[len("```json"):-len("```")]
        print("cleaned response",cleaned_response)
        res_json = json.loads(str(cleaned_response))
    elif not (str_response.startswith("{") and str_response.endswith("}")):
        data = {"response": str_response, "intent": "text"}
        res_json = data
    elif str_response.startswith("{") and str_response.endswith("}"):
        res_json = json.loads(str_response)
    else:
        data = {"response": "Something went wrong, please try again...", "intent": "text"}
        res_json = data

    responseText = ''
    intent = ''
    asset = ''
    amount = ''
    receiverId = ''
    type = ''

    if 'response' in res_json and res_json['response'] is not None:
            responseText += res_json['response']

    if 'intent' in res_json and res_json['intent'] is not None:
        intent += res_json['intent']

    if 'receiverAccount' in res_json and res_json['receiverAccount'] is not None:
        receiverId += res_json['receiverAccount']

    if 'type' in res_json and res_json['type'] is not None:
        type += res_json['type']

    if 'asset' in res_json and res_json['asset'] is not None:  
        asset += res_json['asset']

    if 'amount' in res_json and res_json['amount'] is not None:  
        amount += str(res_json['amount'])

    if res_json['intent'] == "finalJson" and res_json['receiverAccount'] == "":
        responseText = "Please provide the receiver's account."
        intent = "getReceiverId"

    if res_json['intent'] == "finalJson" and res_json['asset'] == "":
        responseText = "Please provide the name of the asset."
        intent = "getAsset"

    if res_json['intent'] == "finalJson" and res_json['amount'] == "":
        responseText = "Please provide the amount of the asset."
        intent = "getAmount"


    data = {"text": responseText, "intent": intent, "meta_data": {"receiverId": receiverId, "token": asset, "value": amount, "operationType": type}}

    return data

# Function - To call chat engine api
# Params - query contains user's query
# return data object response
def retrieval_from_doc(user_id, query):
    memory.chat_store.add_message(key=user_id, message={"role": "user", "content": query})
    data = generate_chat_responses(user_id, str(query))
    return data



def clear_history_from_buffer(user_id):
    memory.chat_store.delete_messages(key=user_id)
    delete_json = {"message": "user " + user_id + " history deleted successfully..."}
    return delete_json