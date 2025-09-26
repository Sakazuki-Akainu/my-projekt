import os
import io
import pandas as pd
import plotly.express as px
from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)
df = None  # global dataframe

HF_TOKEN = os.getenv("HF_TOKEN", None)  # Hugging Face API token (set in Render/Koyeb)

@app.route("/", methods=["GET", "POST"])
def upload_file():
    global df
    if request.method == "POST":
        if "file" not in request.files:
            return "No file uploaded", 400
        file = request.files["file"]
        if file.filename == "":
            return "Empty file", 400

        # Load CSV into dataframe
        df = pd.read_csv(file)
        table_html = df.head().to_html(classes="data", index=False)
        return render_template("upload.html", table=table_html, columns=df.columns)

    return render_template("upload.html", table=None, columns=[])


@app.route("/graph")
def generate_graph():
    global df
    if df is None:
        return jsonify({"error": "No data uploaded"}), 400

    x = request.args.get("x")
    y = request.args.get("y")
    chart_type = request.args.get("type", "line")

    if not x or not y:
        return jsonify({"error": "Missing axis"}), 400

    try:
        if chart_type == "bar":
            fig = px.bar(df, x=x, y=y)
        elif chart_type == "scatter":
            fig = px.scatter(df, x=x, y=y)
        elif chart_type == "pie":
            fig = px.pie(df, names=x, values=y)
        elif chart_type == "box":
            fig = px.box(df, x=x, y=y)
        elif chart_type == "histogram":
            fig = px.histogram(df, x=x)
        else:
            fig = px.line(df, x=x, y=y)

        return jsonify(fig.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/ask", methods=["POST"])
def ask_ai():
    global df
    user_msg = request.json.get("message", "")

    # Summarize dataset for AI
    context = ""
    if df is not None:
        context = f"The dataset has {df.shape[0]} rows and {df.shape[1]} columns. Columns are: {', '.join(df.columns)}."

    if not HF_TOKEN:
        # fallback dummy response
        return jsonify({"reply": f"(Demo AI) You asked: '{user_msg}'. {context}"})

    try:
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        payload = {
            "inputs": f"Context: {context}\nUser question: {user_msg}\nAnswer:"
        }
        resp = requests.post(
            "https://api-inference.huggingface.co/models/google/flan-t5-base",
            headers=headers,
            json=payload,
            timeout=30
        )

        if resp.status_code == 200:
            data = resp.json()
            reply = data[0]["generated_text"]
            return jsonify({"reply": reply})
        else:
            return jsonify({"reply": f"(API error {resp.status_code}) Could not fetch AI response."})
    except Exception as e:
        return jsonify({"reply": f"(Error) {str(e)}"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
