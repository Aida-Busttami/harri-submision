

# AI assistant for harri devs






import json
import os
import glob
from pathlib import Path
from fastapi import FastAPI
import openai
from dotenv import load_dotenv
# Set your OpenAI API key
openai.api_key = "YOUR_OPENAI_API_KEY"
import os
load_dotenv()
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI Assistant")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
# Access variables
api_key = os.getenv("API_KEY")

# Get the directory of the current Python file
current_file_dir = os.path.dirname(os.path.abspath(__file__))
openai.api_key = api_key

# Specify the target directory name that is in the same directory as the current file
target_dir_name = "kb"

# Construct the path to the target directory
kb_path = os.path.join(current_file_dir, target_dir_name)
data_path = os.path.join(current_file_dir, "external_json")

def load_json(filename: str):
    DATA_DIR = Path(data_path)
    filepath = DATA_DIR / filename
    with open(filepath, 'r', encoding='utf-8') as f:
        # assuming file is a JSON array of objects
        data = json.load(f)
    return data

@app.get("/deployments")
def get_deployments():
    data = load_json("DEPLOYMENT.JSON")
    return data
@app.get("/employees")
def get_deployments():
    data = load_json("employees.json")
    return data

@app.get("/jira")
def get_deployments():
    data = load_json("jira_ticktes.json")
    return data



def fetch_api_data():
    urls = {
        "deployments": "http://localhost:8000/deployments",
        "employees": "http://localhost:8000/employees",
        "jira": "http://localhost:8000/jira"
    }
    
    api_data = []
    
    for name, url in urls.items():
        try:
            response = requests.get(url)
            response.raise_for_status()
            json_data = response.json()
            
            for idx, entry in enumerate(json_data):
                text = json.dumps(entry, indent=2)
                api_data.append((f"{name}_{idx}", name, text))  # id, source, content
            
        except Exception as e:
            print(f"Failed to fetch {url}: {e}")
    
    return api_data  # list of tuples (id, source_name, content_str)



def read_md_files(folder_path):
    file_paths = glob.glob(os.path.join(folder_path, '*.md'))
    all_sections = []  # list of (filename, section_title, section_text)
    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
            # Parse markdown headings and split into sections
            # Simple approach: split on lines starting with '#'
            sections = split_into_sections(text)
            for title, content in sections:
                all_sections.append((os.path.basename(file_path), title, content))
    return all_sections

def split_into_sections(md_text):
    """
    Splits markdown text into list of (section_heading, section_content)
    assuming headings start with '#'
    """
    lines = md_text.splitlines()
    sections = []
    current_title = None
    current_content = []

    for line in lines:
        if line.startswith('#'):
            # Save previous section
            if current_title is not None:
                sections.append((current_title, '\n'.join(current_content).strip()))
            current_title = line.lstrip('#').strip()
            current_content = []
        else:
            current_content.append(line)
    # last section
    if current_title is not None:
        sections.append((current_title, '\n'.join(current_content).strip()))
    return sections

def get_embedding(text):
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return response['data'][0]['embedding']

def build_faiss_index(vectors):
    dim = len(vectors[0])
    index = faiss.IndexFlatL2(dim)  # simple L2 index
    index.add(vectors)
    return index

def main():
    folder = kb_path
    data = read_md_files(folder)
    
    # Get embeddings for all sections
    embeddings = []
    metadata = []  # keep track of section identification
    for filename, title, content in data:
        text_for_embedding = f"{title}\n{content}"
        emb = get_embedding(text_for_embedding)
        embeddings.append(emb)
        metadata.append({'file': filename, 'title': title, 'content': content})

    import numpy as np
    vectors = np.array(embeddings).astype('float32')

    index = build_faiss_index(vectors)

    # Save index and metadata
    faiss.write_index(index, "faiss_index.bin")
    import json
    with open("metadata.json", "w", encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print("FAISS index and metadata saved.")

    # I need to 




    def __init__(self):
        self.name = "AI Assistant"