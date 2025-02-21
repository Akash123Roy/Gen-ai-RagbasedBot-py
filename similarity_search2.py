from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import google.generativeai as genai
from data_extraction import DataExtraction
from prompt_templates import PromptTemplate
from data_chunk import DataChunk
from pymongo import MongoClient
from flask import Flask, request, jsonify
# from werkzeug.utils import secure_filename
# from io import BytesIO
# import os
from flask_cors import CORS



# Initialize the model (you can change this to any transformer model you prefer)
generative_models = genai.GenerativeModel('models/gemini-2.0-flash-exp')
model = SentenceTransformer('multi-qa-mpnet-base-dot-v1')
API_KEY= ""
genai.configure(api_key=API_KEY)
file_path = 'selfish_giant_story.txt'
data = DataExtraction(file_path)
connection_string = 'mongodb://localhost:27017/'
app = Flask(__name__)
chunk = DataChunk()
prompt = PromptTemplate()
CORS(app)

#mongo connection details
client = MongoClient(connection_string)
db = client['RAG_Database']
collection = db['Data_embedding']

doc_data = data.process_file().replace("'", "").replace('"', "").replace("\n", " ")
# print(doc_data)
data_chunk = chunk.create_data_chunk(doc_data)

# Embed the stored content (story sections)
stored_embeddings = np.array([model.encode(sentence) for sentence in data_chunk])
converted_embedding = stored_embeddings.tolist()
collection.update_one(
    {"content": data_chunk},
    {
        "$set":{
            "Embedding": converted_embedding
        }
    },
    upsert = True
)

retriev_data = list(collection.find({},{"_id":0}))
content = []
embedding = []
for dic in retriev_data:
    for key, val in dic.items():
        if key == "content":
            content.extend(val)
            print(content)
        elif key == "Embedding":
            embedding.extend(val)

vector_embedding = np.array(embedding)
print(f"vector embedding shape: {vector_embedding.shape}")
if vector_embedding.ndim != 2:
    print("Not a 2D array")
else:
    print("2D array")


@app.route("/generate", methods = ["POST"])
def generate_response():
    try:
        
        query = request.json.get("query")
        query_data = query.lower()
        print(query)
        if not query:
            return jsonify({"error":"query is required"}),400
        query_embedding = model.encode(query_data)
        final_query_embedding = np.array(query_embedding)
        print(f"final query embedding shape: {final_query_embedding.shape}")

        # Compute cosine similarity between query and stored content embeddings
        similarities = cosine_similarity([final_query_embedding], vector_embedding)[0]

        # Get the top N most similar sentences
        top_n = 3  # You can adjust this based on the number of relevant results you want
        top_indices = np.argsort(similarities)[::-1][:top_n]
        top_indices.sort()

        # Display the most relevant content based on similarity
        contents = []
        for index in top_indices:
            contents.append(content[index])
        full_content = " ".join(contents)
        prompt_data = prompt.make_prompt(query_data, full_content)
        answer = generative_models.generate_content(prompt_data)
        response = answer.text
        response = response.replace("'", "").replace('"', "").replace("\n", " ")
        return jsonify({"Response": response})
    except Exception as e:
        return jsonify({"error": str(e)}),500
    
if __name__ == "__main__":
    app.run(debug = True)
