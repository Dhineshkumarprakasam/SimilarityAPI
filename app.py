import os
import numpy as np
import json
import uuid
from datetime import datetime
import spacy
from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask, request, jsonify
import sqlitecloud

app = Flask(__name__)
nlp = spacy.load("en_core_web_md")

# ------------------ Load DB Connection from Environment ------------------ #
DB_PATH = os.getenv("SQLITE_CLOUD_URL")

# ------------------ Utility Functions ------------------ #
def keep_nouns_adjs(text):
    doc = nlp(text)
    tokens = [
        token.lemma_.lower()
        for token in doc
        if token.pos_ in ["NOUN", "PROPN", "ADJ"] and not token.is_stop and not token.is_punct
    ]
    return " ".join(tokens)

def text_to_vector(text):
    clean_text = keep_nouns_adjs(text)
    doc = nlp(clean_text)
    return doc.vector

# ------------------ Vector Database Class ------------------ #
class VectorDatabase:
    def __init__(self, db_path, similarity_threshold=0.7):
        self.similarity_threshold = similarity_threshold
        self.db_path = db_path
        self._init_db()

    def _connect(self):
        return sqlitecloud.connect(self.db_path)

    def _init_db(self):

        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vector_database (
                id TEXT PRIMARY KEY,
                text TEXT NOT NULL,
                vector TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def add_or_find_duplicate(self, text):
        new_vector = text_to_vector(text)
        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute("SELECT id, text, vector, timestamp FROM vector_database")
        rows = cursor.fetchall()

        for row in rows:
            entry_id, entry_text, entry_vector_json, timestamp = row
            entry_vector = np.array(json.loads(entry_vector_json))
            sim = cosine_similarity(new_vector.reshape(1, -1), entry_vector.reshape(1, -1))[0][0]
            if sim >= self.similarity_threshold:
                conn.close()
                return {
                    'status': 'duplicate',
                    'similarity': sim,
                    'id': entry_id,
                    'text': entry_text,
                    'timestamp': timestamp
                }

        entry_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().isoformat()
        cursor.execute(
            "INSERT INTO vector_database (id, text, vector, timestamp) VALUES (?, ?, ?, ?)",
            (entry_id, text, json.dumps(new_vector.tolist()), timestamp)
        )
        conn.commit()
        conn.close()
        return {
            'status': 'added',
            'id': entry_id,
            'text': text,
            'timestamp': timestamp
        }

# ------------------ Flask API ------------------ #
db = VectorDatabase(DB_PATH, similarity_threshold=0.5)

@app.route("/similarity", methods=["POST"])
def similarity():
    try:
        data = request.json.get("data", "")
        result = db.add_or_find_duplicate(data)
        if result['status'] == 'duplicate':
            return jsonify({
                "status": result['status'],
                "id": result['id'],
                "text": result['text'],
                "timestamp": result['timestamp'],
                "score": str(round(result['similarity'], 2))
            })
        else:
            return jsonify({
                "status": result['status'],
                "id": result['id'],
                "text": result['text'],
                "timestamp": result['timestamp']
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run()
