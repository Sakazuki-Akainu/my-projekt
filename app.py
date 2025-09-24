import requests
from flask import Flask, render_template, request, jsonify
import pandas as pd
import plotly.express as px
import os

app = Flask(__name__)

# store last uploaded dataframe for AI chat
current_df = None

# HuggingFace API setup (replace with your token if you make account)
HF_TOKEN = os.getenv("HF_TOKEN", None)  # set via Render env vars
HF_MODEL = "google/flan-t5-small"       # lightweight free model

def ask_huggingface(question, context):
    if not HF_TOKEN:
        return "(No HuggingFace token set, cannot call API)"
    payload = {"inputs": f"Context: {context}\nQuestion: {question}"}
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    r = requests.post(f"https://api-inference.huggingface.co/models/{HF_MODEL}", headers=headers, json=payload)
    if r.status_code == 200:
        return r.json()[0]["generated_text"]
    else:
        return f"(Error {r.status_code} from HuggingFace)"

@app.route("/", methods=["GET", "POST"])
def upload_file():
    global current_df
    if request.method == "POST":
        file = request.files["file"]
        if file:
            df = pd.read_csv(file)
            current_df = df  # store for chat use

            # Table
            table_html = df.head().to_html(classes="table table-striped", index=False)

            # Graph
            numeric_cols = df.select_dtypes(include="number").columns
            if len(numeric_cols) >= 2:
                fig = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1], title="Scatter Plot")
            elif len(numeric_cols) == 1:
                fig = px.histogram(df, x=numeric_cols[0], title="Distribution")
            else:
                fig = px.histogram(df, x=df.columns[0], title="Counts")
            graph_html = fig.to_html(full_html=False)

            return render_template("upload.html", table=table_html, graph=graph_html, insights=None)
    return render_template("upload.html", table=None, graph=None, insights=None)

@app.route("/ask", methods=["POST"])
def ask():
    global current_df
    data = request.get_json()
    question = data.get("question", "")
    if current_df is None:
        return jsonify({"answer": "Please upload a dataset first."})

    # turn dataframe into small context string
    context = current_df.head(10).to_csv(index=False)

    if HF_TOKEN:
        answer = ask_huggingface(question, context)
    else:
        # fallback: rule-based
        answer = f"(Demo) Your question was: {question}. Currently only rule-based answers available."

    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
