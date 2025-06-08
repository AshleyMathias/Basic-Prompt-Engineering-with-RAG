import os
from tkinter import *
from tkinter import filedialog, messagebox, scrolledtext

from langchain.document_loaders import PyPDFLoader, TextLoader
from langchain_community.document_loaders import PyPDFLoader, TextLoader

from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from dotenv import load_dotenv

load_dotenv()  # Load your OPENAI_API_KEY from .env file

class RAGApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Basic Prompt Engineering with RAG")
        self.root.geometry("700x600")

        # Variables
        self.file_path = ""
        self.vectorstore = None

        # UI Elements
        Label(root, text="Select Document (PDF or TXT):", font=("Arial", 12)).pack(pady=5)
        Button(root, text="Browse File", command=self.browse_file).pack(pady=5)

        self.file_label = Label(root, text="No file selected", fg="red")
        self.file_label.pack()

        Label(root, text="Enter your prompt/question:", font=("Arial", 12)).pack(pady=10)
        self.prompt_entry = Entry(root, width=80)
        self.prompt_entry.pack(pady=5)

        Button(root, text="Run Query", command=self.run_query).pack(pady=10)

        Label(root, text="Answer:", font=("Arial", 12)).pack(pady=5)
        self.answer_area = scrolledtext.ScrolledText(root, height=15, width=80, wrap=WORD)
        self.answer_area.pack(pady=5)

    def browse_file(self):
        filetypes = (("PDF files", "*.pdf"), ("Text files", "*.txt"))
        filepath = filedialog.askopenfilename(filetypes=filetypes)
        if filepath:
            self.file_path = filepath
            self.file_label.config(text=os.path.basename(filepath), fg="green")
            self.load_vectorstore()

    def load_vectorstore(self):
        try:
            # Load document based on file type
            if self.file_path.endswith(".pdf"):
                loader = PyPDFLoader(self.file_path)
            elif self.file_path.endswith(".txt"):
                loader = TextLoader(self.file_path)
            else:
                messagebox.showerror("Unsupported file", "Please select a PDF or TXT file.")
                return

            documents = loader.load()

            # Split text to chunks
            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            docs = text_splitter.split_documents(documents)

            # Create embeddings and vectorstore (FAISS)
            embeddings = OpenAIEmbeddings()
            self.vectorstore = FAISS.from_documents(docs, embeddings)

            messagebox.showinfo("Success", "Document loaded and processed successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load document: {e}")

    def run_query(self):
        if not self.vectorstore:
            messagebox.showwarning("No document", "Please load a document first.")
            return

        question = self.prompt_entry.get()
        if not question.strip():
            messagebox.showwarning("Empty prompt", "Please enter a prompt/question.")
            return

        try:
            # Setup LLM and retrieval QA chain
            llm = OpenAI(temperature=0)
            qa = RetrievalQA.from_chain_type(llm=llm, retriever=self.vectorstore.as_retriever())

            # Run query and get answer
            answer = qa.run(question)
            self.answer_area.delete(1.0, END)
            self.answer_area.insert(END, answer)
        except Exception as e:
            messagebox.showerror("Query Error", f"Failed to run query: {e}")

if __name__ == "__main__":
    root = Tk()
    app = RAGApp(root)
    root.mainloop()
