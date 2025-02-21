from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import google.generativeai as genai
from data_extraction import DataExtraction
from prompt_templates import PromptTemplate
from data_chunk import DataChunk
from pymongo import MongoClient
from flask import Flask, request, jsonify, render_template
# from werkzeug.utils import secure_filename
import os
from flask_cors import CORS
import traceback

# Initialize the model (you can change this to any transformer model you prefer)
generative_models = genai.GenerativeModel('models/gemini-2.0-flash-exp')
model = SentenceTransformer('multi-qa-mpnet-base-dot-v1')

API_KEY= "AIzaSyBjKe4Wk6CUtT0oSG1pUaq4Sn0ER90JpGY"
# Configure the API key for Google Generative AI
genai.configure(api_key=API_KEY)  # Replace with your actual API key

# Initialize data extraction and MongoDB connection
connection_string = 'mongodb://localhost:27017/'
app = Flask(__name__)

# MongoDB connection details
client = MongoClient(connection_string)
db = client['RAG_Database']
collection = db['Data_embedding']

# Create an instance of DataExtraction and DataChunk
chunk = DataChunk()
prompt = PromptTemplate()



UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
 #Ensure the upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def login():
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route("/upload", methods=["POST"])
def upload_file():

    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        if file and allowed_file(file.filename):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            # print(file_path)
            data_extraction = DataExtraction(file_path)
            
            # Process the uploaded file
            doc_data = data_extraction.process_file().replace("'", "").replace('"', "").replace("\n", " ")
            # print(f"complete data: {doc_data}"")
            data_chunk = chunk.create_data_chunk(doc_data)
            # print(f"data_chunk: {data_chunk}")

            # Embed the stored content (story sections)
            stored_embeddings = np.array([model.encode(sentence) for sentence in data_chunk])
            converted_embedding = stored_embeddings.tolist()
            collection.update_one(
                {"content": data_chunk},
                {
                    "$set": {
                        "Embedding": converted_embedding
                    }
                },
                upsert=True
            )
            print("Data uploaded to MongoDB successfully.")
    except Exception as e:
        return jsonify({f"error:{str(e)}"})

            
@app.route('/query', methods=['POST'])
def process_query():
    try:
        # Retrieve data from MongoDB
        retriev_data = list(collection.find({}, {"_id": 0}))
        content = []
        embedding = []
        for dic in retriev_data:
            for key, val in dic.items():
                if key == "content":
                    content.extend(val)
                    # print(f"content: {content}")
                elif key == "Embedding":
                    embedding.extend(val)
        vector_embedding = np.array(embedding)
        if vector_embedding.ndim == 2:
            print(f"Embedding is a 2D array of shape: {vector_embedding.shape}")
        data = request.get_json()
        query = data.get('query', '').strip()
        print(query)
        if not query:
            return jsonify({'response': 'Query cannot be empty.'}), 400
        query_data = query.lower()
        query_embedding = model.encode(query_data)
        final_query_embedding = np.array(query_embedding)
        print(f"query shape: {final_query_embedding.shape}")
        print(traceback.format_exc())
        # print(f"similarity check: {content}")

        similarities = cosine_similarity([final_query_embedding], vector_embedding)[0]
        # print(f"cosine similaity: {similarities}")

        # Get the top N most similar sentences
        top_n = 5  # Adjust based on the number of relevant results you want
        top_indices = np.argsort(similarities)[::-1][:top_n]
        top_indices.sort()
        # print(f"top indices: {top_indices}")

        # Display the most relevant content based on similarity
        contents = []
        for index in top_indices:
            contents.append(content[index])
        print(f"contents are: {contents}")
        full_content = " ".join(contents)
        prompt_data = prompt.make_prompt(query_data, full_content)
        answer = generative_models.generate_content(prompt_data)
        response = answer.text
        response = response.replace("'", "").replace('"', "").replace("\n", " ")
        print(traceback.format_exc())
        print(f"response is: {response}")
        return jsonify({"Response": response}),200

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug = True)
    