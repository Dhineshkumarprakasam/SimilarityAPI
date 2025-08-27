from flask import Flask, request, jsonify
import spacy

app = Flask(__name__)
nlp = spacy.load("en_core_web_md")

def keep_nouns_adjs(text):
    doc = nlp(text)
    tokens = [
        token.lemma_.lower()
        for token in doc
        if token.pos_ in ["NOUN", "PROPN", "ADJ"] and not token.is_stop and not token.is_punct
    ]
    return " ".join(tokens)

@app.route("/similarity", methods=["POST"])
def similarity():
    try:
        data = request.json
        existing = data.get("existing", "")
        user = data.get("user", "")

        # Clean texts
        clean_existing = keep_nouns_adjs(existing)
        clean_user = keep_nouns_adjs(user)

        # Re-run similarity
        doc1 = nlp(clean_existing)
        doc2 = nlp(clean_user)
        score = doc1.similarity(doc2)

        return jsonify({
            "similarity_score": round(float(score), 4)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
