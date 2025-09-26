import os
import pandas as pd
import plotly.express as px
from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)
df = None  # currently loaded dataframe (in-memory)

# Hugging Face token (set as environment variable in Render/Koyeb)
HF_TOKEN = os.environ.get("HF_TOKEN", None)
HF_MODEL = "google/flan-t5-base"  # a lightweight text model on HF inference

@app.route("/", methods=["GET", "POST"])
def index():
    global df
    if request.method == "POST":
        # file upload
        if "file" not in request.files:
            return "No file uploaded", 400
        file = request.files["file"]
        if file.filename == "":
            return "Empty filename", 400

        # Attempt to read CSV or Excel
        try:
            filename = file.filename.lower()
            if filename.endswith(".csv"):
                df = pd.read_csv(file)
            elif filename.endswith((".xls", ".xlsx")):
                df = pd.read_excel(file)
            else:
                # try CSV by default
                df = pd.read_csv(file)
        except Exception as e:
            return f"Failed to read file: {e}", 400

        # prepare small preview + columns for front-end selects
        table_html = df.head(50).to_html(classes="table table-striped table-bordered", index=False)
        columns = list(df.columns)
        return render_template("upload.html", table=table_html, columns=columns)

    # GET
    return render_template("upload.html", table=None, columns=[])


@app.route("/graph")
def graph():
    """
    Create a Plotly figure based on query parameters and return the figure as a dict
    so the browser can render via Plotly.newPlot(data, layout)
    query params: x, y, type
    """
    global df
    if df is None:
        return jsonify({"error": "No dataset loaded. Upload a CSV first."}), 400

    x = request.args.get("x")
    y = request.args.get("y")
    chart_type = request.args.get("type", "line")

    if not x:
        return jsonify({"error": "Missing x parameter"}), 400

    try:
        if chart_type == "bar":
            fig = px.bar(df, x=x, y=y) if y else px.histogram(df, x=x)
        elif chart_type == "scatter":
            if not y:
                return jsonify({"error": "Scatter requires y parameter"}), 400
            fig = px.scatter(df, x=x, y=y)
        elif chart_type == "pie":
            if not y:
                return jsonify({"error": "Pie requires values (y) parameter"}), 400
            fig = px.pie(df, names=x, values=y)
        elif chart_type == "box":
            fig = px.box(df, x=x, y=y) if y else px.box(df, y=x)
        elif chart_type == "histogram":
            fig = px.histogram(df, x=x)
        else:  # default line
            if not y:
                return jsonify({"error": "Line chart requires y parameter"}), 400
            fig = px.line(df, x=x, y=y)

        # return full figure as JSON compatible dict
        return jsonify(fig.to_dict())
    except Exception as e:
        return jsonify({"error": f"Failed to create chart: {e}"}), 500


def hf_inference(prompt: str, model: str = HF_MODEL, token: str = HF_TOKEN, timeout: int = 30):
    """
    Ask HuggingFace Inference API a prompt. Returns string response or raises.
    """
    if not token:
        raise RuntimeError("No HF token provided.")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"inputs": prompt}
    url = f"https://api-inference.huggingface.co/models/{model}"
    r = requests.post(url, headers=headers, json=payload, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    # response can sometimes be list/dict depending on model
    if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
        # e.g. [{"generated_text":"..."}]
        return data[0].get("generated_text") or data[0].get("text") or str(data[0])
    if isinstance(data, dict) and "generated_text" in data:
        return data["generated_text"]
    # fallback: stringify
    return str(data)


def rule_based_answer(question: str, local_df: pd.DataFrame):
    """
    Basic, safe fallback answer generator using pandas. Not a full NLU model,
    but handles common requests (average, median, top, count, columns).
    """
    q = question.lower()
    numeric = local_df.select_dtypes(include="number")
    text = []

    # generic summary
    text.append(f"The dataset has {local_df.shape[0]} rows and {local_df.shape[1]} columns.")
    text.append("Columns: " + ", ".join(local_df.columns[:10]) + ("..." if local_df.shape[1] > 10 else ""))

    # numeric stats
    if len(numeric.columns) > 0:
        stats = numeric.describe().round(3)
        # If user asked for average/mean/median/min/max keywords, return them
        if any(k in q for k in ["average", "mean", "median", "min", "max", "top", "highest", "lowest"]):
            for col in numeric.columns[:5]:
                text.append(f"{col}: mean={stats[col]['mean']}, median={numeric[col].median():.3f}, min={stats[col]['min']}, max={stats[col]['max']}.")
        else:
            # default summary for numeric columns
            for col in numeric.columns[:5]:
                text.append(f"{col}: mean={stats[col]['mean']}, std={stats[col]['std']:.3f}.")
    else:
        # non-numeric: show top values of first two columns
        for col in local_df.columns[:2]:
            vals = local_df[col].value_counts().head(5).to_dict()
            text.append(f"Top values for {col}: {vals}")

    # if the user asks to compare two columns: detect "vs" or "compare"
    if " vs " in q or "compare" in q:
        # try to pick two numeric columns
        if len(numeric.columns) >= 2:
            c1, c2 = numeric.columns[:2]
            m1, m2 = numeric[c1].mean(), numeric[c2].mean()
            comp = f"{c1} has mean {m1:.2f}, {c2} has mean {m2:.2f}. " + (f"{c1} > {c2}" if m1 > m2 else f"{c2} >= {c1}")
            text.append(comp)
    return " ".join(text)


@app.route("/ask", methods=["POST"])
def ask():
    """
    Chat endpoint. Accepts JSON: {"message": "..."}
    Returns: {"reply": "..."}
    """
    global df
    data = request.get_json(force=True)
    user_msg = data.get("message") or data.get("question") or ""
    if not user_msg:
        return jsonify({"reply": "No question received."})

    # small context: first 10 rows as CSV snippet
    context = ""
    if df is not None:
        snippet = df.head(10).to_csv(index=False)
        context = f"Dataset preview (first 10 rows):\n{snippet}\n\n"

    # if HF token present, try HF inference
    if HF_TOKEN:
        prompt = f"{context}\nUser: {user_msg}\nAssistant: Provide a concise, factual answer based only on the dataset context above (if relevant)."
        try:
            resp_text = hf_inference(prompt)
            return jsonify({"reply": resp_text})
        except Exception as e:
            # return fallback but include error in logs
            print("HF inference failed:", e)

    # fallback rule-based
    fallback = rule_based_answer(user_msg, df) if df is not None else "(No dataset loaded) " + user_msg
    return jsonify({"reply": f"(Fallback) {fallback}"})


if __name__ == "__main__":
    # Render/Koyeb bind
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
