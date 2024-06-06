import streamlit as st 
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import OpenAIEmbeddings
from concurrent.futures import ThreadPoolExecutor
from methods import orchestrate_response_and_upload, orchestration_pdf_vectore_store, get_context_retriever_chain, get_conversational_rag_chain, init_mongodb_connection, get_systems_health


#app config
st.set_page_config(page_title="Medicall Support", page_icon="ℹ️")
st.title("Medicall Support")

#initialize mongodb and embeddingsmodel for validation
if "collection" not in st.session_state:
     st.session_state.collection = init_mongodb_connection()

if "embeddings" not in st.session_state:
     st.session_state.embeddings = OpenAIEmbeddings()

#this is used to get cosine similarity. 
with st.sidebar:
    if st.button("Systemstatus prüfen"):
        health_status = get_systems_health(st.session_state.collection)
        st.write(health_status)
    else:
        st.write("Klicken Sie auf die Schaltfläche, um den Systemstatus zu prüfen.")

with st.sidebar:
     st.write("Systemstatus wird nicht automatisch aktualisiert. Klicken Sie auf die Schaltfläche, um den aktuellen Systemstatus zu prüfen.")

#initialize pdf and get vectore store. Update path to run. This is not efficent, everytime i run the application the method is going to run, even if the store already exists. I know, i need to improve this. 
#at the end of the day this is a prototype.     
pdf = r"C:\Users\Admin\Desktop\ML2\Final_Project\src\Leistungen.pdf"
if "vectore_store" not in st.session_state:
     st.session_state.vector_store = orchestration_pdf_vectore_store(pdf)
#get the context needed to answer the question
retriever_chain = get_context_retriever_chain(st.session_state.vector_store)
#connect the chains together 
conversational_rag_chain = get_conversational_rag_chain(retriever_chain)

#chat history using langchain schema and making it persistent during our session. If this is not done
#we will not be able to get a sense of conversational capacity it is also pivotal for the chains. 
#Streamlit uploads our file consistenly so chat_history would be reinitiated everytime.

if "chat_history" not in st.session_state:
     st.session_state.chat_history = [
     AIMessage(content="Hey! Wie kann ich dir helfen?"),
     ]

#user input
user_query = st.chat_input("Schreibe hier deine Fragen")
if user_query is not None and user_query !="":
        with st.spinner("Wir bereiten die beste Antwort vor ⏳"):
          response = orchestrate_response_and_upload(st.session_state.chat_history, conversational_rag_chain, user_query, st.session_state.collection, st.session_state.embeddings)
          st.session_state.chat_history.append(HumanMessage(content=user_query))
          st.session_state.chat_history.append(AIMessage(content=response))

#conversation
for message in st.session_state.chat_history:
     if isinstance(message, AIMessage):
          with st.chat_message("AI"):
               st.write(message.content)
     elif isinstance(message, HumanMessage):
            with st.chat_message("Human"):
                st.write(message.content)
      

