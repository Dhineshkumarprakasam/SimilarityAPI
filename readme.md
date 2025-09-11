# Similarity Text Detection API

This project is a **Flask-based REST API** that detects duplicate or highly similar text entries using **SpaCy embeddings** and stores them in a **SQLite Cloud database**.  
It is useful for applications like content Similarity, knowledge-base cleanup, or detecting near-duplicate user submissions.

---

## Features
- Extracts **nouns and adjectives** from input text to build clean embeddings.
- Uses **SpaCy (`en_core_web_md`)** word vectors for semantic similarity.
- Stores text + embeddings + timestamp in **SQLite Cloud**.
- Detects duplicates based on **cosine similarity** (configurable threshold).
- REST API endpoint (`/similarity`) to:
  - Add new text
  - Identify if it is a **duplicate** of an existing entry

---

## Project Structure
```

.
├── app.py              # Main Flask app with API and DB logic
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation

````

---

## Installation & Setup

### 1. Clone Repository
```bash
git clone https://github.com/your-username/duplicate-text-detection.git
cd duplicate-text-detection
````

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # On Linux/Mac
venv\Scripts\activate      # On Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Download SpaCy Model

```bash
python -m spacy download en_core_web_md
```

### 5. Set Environment Variable for SQLite Cloud

```bash
export SQLITE_CLOUD_URL="your_sqlite_cloud_connection_string"
```

\*(On Windows PowerShell: `setx SQLITE_CLOUD_URL "your_connection_string"`)

---

## Running the API

```bash
python app.py
```

By default, the API runs at:
`http://127.0.0.1:5000`

---

## API Usage

### Endpoint: `/similarity` (POST)

Check and/or add a text entry to the database.

#### Request

```json
{
  "data": "Artificial Intelligence improves agriculture productivity."
}
```

#### Responses

**New Entry Added**

```json
{
  "status": "added",
  "id": "a1b2c3d4",
  "text": "Artificial Intelligence improves agriculture productivity.",
  "timestamp": "2025-09-11T14:05:23.123456"
}
```

**Duplicate Found**

```json
{
  "status": "duplicate",
  "id": "x9y8z7w6",
  "text": "AI helps in agriculture productivity",
  "timestamp": "2025-09-11T12:00:00.000000",
  "score": "0.87"
}
```

---

## Configuration

* **Similarity Threshold** (default `0.5`)
  Modify in `VectorDatabase(DB_PATH, similarity_threshold=0.5)` to adjust strictness.

---

## Dependencies

* Python 3.8+
* Flask
* SpaCy (`en_core_web_md`)
* NumPy
* scikit-learn
* sqlitecloud

---

## Future Improvements

* Add **authentication** for API access.
* Support **batch similarity checks**.
* Add option for different **embedding models**.
* Deploy on **Docker** or **Cloud Run** for production use.

---

## License

This project is licensed under the MIT License.
