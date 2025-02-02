import os
from dotenv import load_dotenv
import json
import ollama
from langchain_ollama.llms import OllamaLLM

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter, RecursiveJsonSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain import hub




def chatbot(input_prompt):
    model_name = "sentence-transformers/all-mpnet-base-v2"
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': False}
    hf = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )
    
    
    with open('helpful_info.json', 'r') as file:
        files = json.load(file)
    
    
    def clean_and_format_data(data,selected_fields):
        formatted_data = {}
    
        for category, records in data.items():
            cleaned_records = []
    
            for record in records:
                cleaned_record = {
                    k.lstrip("#").split("\\n")[0].split("\n")[0].strip(): v.lstrip("#").split("\\n")[0].strip()
                    # Remove `#`, `\n`, and extra spaces
                    for k, v in record.items()
                    if v.strip().lower() not in ["nan", ""]  # Remove empty or 'nan' values
                }
                
                # Keep only selected fields
                filtered_record = {
                    key: value for key, value in cleaned_record.items() if key in selected_fields
                }
    
                if filtered_record:  # Only add records with selected fields
                    cleaned_records.append(filtered_record)
    
            if cleaned_records:  # Only add categories with valid records
                formatted_data[category] = cleaned_records
    
        return formatted_data
    
    cleaned_data = clean_and_format_data({"Offers": files["Offers"],"Sub-Categories": files["Sub-Categories"]},
                                         ["Unnamed: 0", 'Unique URL (only "a-z 0-9" or "-")',
                                          'Phone Number','Sub-Category Description','Opening Hours Weekdays',
                                          'Opening Hours Weekends','What do you need to know?','Added on (date)'])
    
    with open('data_cleaned.json', 'w') as f:
        json.dump(cleaned_data, f)
    
    
    text_splitter = RecursiveJsonSplitter(max_chunk_size=300)
    docs = text_splitter.create_documents(texts=[cleaned_data])
    
    embeddings = hf
    vectorstore = FAISS.from_documents(docs, embeddings)
    
    # Save the vector store
    vectorstore.save_local("faiss_index")
    
    # Load the vector store
    new_vectorstore = FAISS.load_local(
           "faiss_index", embeddings, allow_dangerous_deserialization=True
       )
    new_vectorstore
    
    
    retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")
    
    combine_docs_chain = create_stuff_documents_chain(
           OllamaLLM(model = 'deepseek-r1:latest'), retrieval_qa_chat_prompt
       )
    
    retrieval_chain = create_retrieval_chain(
           new_vectorstore.as_retriever(), combine_docs_chain
       )
    
    res = retrieval_chain.invoke({"input": input_prompt})
    return res["answer"]