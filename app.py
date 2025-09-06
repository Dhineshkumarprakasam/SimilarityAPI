import numpy as np
import json
import uuid
from datetime import datetime
import spacy
from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask, request, jsonify
import spacy


app = Flask(__name__)
nlp = spacy.load("en_core_web_md") 

def keep_nouns_adjs(text):
    #Return a lemmatized string of nouns, proper nouns, adjectives (no stopwords).
    doc = nlp(text)
    tokens = [
        token.lemma_.lower()
        for token in doc
        if token.pos_ in ["NOUN", "PROPN", "ADJ"] and not token.is_stop and not token.is_punct
    ]
    return " ".join(tokens)


def text_to_vector(text):
    #Convert text to a spaCy vector based on filtered nouns/adjectives.
    clean_text = keep_nouns_adjs(text)
    doc = nlp(clean_text)
    return doc.vector  # returns a fixed-length vector (300-dim for en_core_web_md)


class VectorDatabase:
    def __init__(self, similarity_threshold=0.7):
        self.similarity_threshold = similarity_threshold
        self.database = {}  # {id: {'text': str, 'vector': np.array, 'timestamp': str}}

    def add_or_find_duplicate(self, text):
        new_vector = text_to_vector(text)
        for entry_id, entry_data in self.database.items():
            sim = cosine_similarity(
                new_vector.reshape(1, -1), entry_data['vector'].reshape(1, -1)
            )[0][0]
            if sim >= self.similarity_threshold:
                # Return the existing entry info
                return {
                    'status': 'duplicate',
                    'similarity': sim,
                    'id': entry_id,
                    'text': entry_data['text'],
                    'timestamp': entry_data['timestamp']
                }

        # Add new text
        entry_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().isoformat()
        self.database[entry_id] = {
            'text': text,
            'vector': new_vector,
            'timestamp': timestamp
        }
        return {
            'status': 'added',
            'id': entry_id,
            'text': text,
            'timestamp': timestamp
        }

    def export_database(self, filepath="vector_db.json"):
        export_data = {
            eid: {
                'text': e['text'],
                'vector': e['vector'].tolist(),
                'timestamp': e['timestamp']
            } for eid, e in self.database.items()
        }
        with open(filepath, 'w') as f:
            json.dump(export_data, f)

    def import_database(self, filepath="vector_db.json"):
        with open(filepath, 'r') as f:
            import_data = json.load(f)
        self.database = {
            eid: {
                'text': e['text'],
                'vector': np.array(e['vector']),
                'timestamp': e['timestamp']
            } for eid, e in import_data.items()
        }


@app.route("/similarity", methods=["POST"])
def similarity():
    try:
        data = request.json.get("data", "")
        result = db.add_or_find_duplicate(data)
        if result['status'] == 'added':
            db.export_database("vector_db.json")

        if result['status'] == 'duplicate':
            return jsonify({
                "status":result['status'],
                "id":result['id'],
                "text":result['text'],
                "timestamp":result['timestamp'],
                "score":str(round(result['similarity'],2))
            })
        else:
             return jsonify({
                 "status":result['status']
             })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    db = VectorDatabase(similarity_threshold=0.6)
    # Load previous database if exists
    try:
        db.import_database("vector_db.json")
    except:
        pass
    app.run()
