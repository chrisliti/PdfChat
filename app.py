import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings#, HuggingFaceInstructEmbeddings
from langchain.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from htmlTemplates import css, bot_template, user_template



def get_conversation_chain(vector_store):

    llm = ChatOpenAI()

    memory = ConversationBufferMemory(memory_key = 'chat_history',return_messages=True)

    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm = llm,
        retriever = vector_store.as_retriever(),
        memory = memory

    )

    return conversation_chain

    


def get_vectorstore (text_chunks):

    embeddings = OpenAIEmbeddings()

    #embeddings = HuggingFaceInstructEmbeddings(model_name = "hkunlp/instructor-xl")

    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)

    return vectorstore



def get_text_chunks(text):

    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )

    chunks = text_splitter.split_text(text)
    return chunks


def get_pdf_text(pdf_docs):

    text = ""

    for pdf in pdf_docs:

        pdf_reader = PdfReader((pdf))

        for page in pdf_reader.pages:

            text += page.extract_text()

    return text





def main():

    load_dotenv()

    st.set_page_config(page_title="Chat with multiple PDF's",page_icon=":books:")

    st.write(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state:

        st.session_state.conversation = None

    st.header("Chat with multiple PDFs :books:")
    st.text_input("Ask a question about your documents:")

    st.write(user_template.replace("{{MSG}}", "Hello robot"), unsafe_allow_html=True)
    st.write(bot_template.replace("{{MSG}}", "Hello robot"), unsafe_allow_html=True)


    with st.sidebar:
        st.subheader("Your documents")
        pdf_docs = st.file_uploader("Upload your PDFs here and click on 'process'",accept_multiple_files=True)
        
        if st.button("Process"):

            with st.spinner("Processing"):

                ## Get pdf text

                raw_text = get_pdf_text(pdf_docs)

                ## Get the text chunks

                text_chunks = get_text_chunks(raw_text)

                ## Create vector store

                vector_store = get_vectorstore(text_chunks)

                ## Create conversation chain

                st.session_state.conversation = get_conversation_chain(vector_store)



    

        


if __name__ == '__main__':
    main()