from flask import Flask, render_template, request, jsonify
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # for servers without display
import matplotlib.pyplot as plt
import io, base64, os, json
import requests

app = Flask(__name__)

# =====================
# ROUTES
# =====================

@app.route("/")
def index():
    return render_template("upload.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    try:
        df = pd.read_csv(file)
        # Convert DataFrame preview to HTML
        preview_html = df.head().to_html(classes="table table-striped", index=False)
        # Convert column names for dropdowns
        columns = df.columns.tolist()
        return jsonify({"preview": preview_html, "columns": columns})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/graph", methods=["POST"])
def generate_graph():
    try:
        data = request.json
        df = pd.DataFrame(data["data"])
        x = data["x"]
        y = data["y"]
        chart_type = data["chart"]

        plt.figure(figsize=(6, 4))
        if chart_type == "line":
            plt.plot(df[x], df[y])
        elif chart_type == "bar":
            plt.bar(df[x], df[y])
        elif chart_type == "scatter":
            plt.scatter(df[x], df[y])
        elif chart_type == "pie":
            plt.pie(df[y], labels=df[x], autopct="%1.1f%%")

        plt.xlabel(x)
        plt.ylabel(y)
        plt.title(f"{chart_type.capitalize()} Chart")

        # Save image to base64
        img = io.BytesIO()
        plt.savefig(img, format="png")
        img.seek(0)
        graph_url = base64.b64encode(img.getvalue()).decode()
        plt.close()
        return jsonify({"graph": f"data:image/png;base64,{graph_url}"})
    except Exception as e:
        return jsonify({"error": f"Graph error: {str(e)}"}), 500


@app.route("/ask", methods=["POST"])
def ask_ai():
    try:
        user_input = request.json.get("question", "")
        if not user_input:
            return jsonify({"answer": "Please ask a question."})

        # Try Hugging Face or OpenAI if token available
        hf_token = os.getenv("HF_TOKEN")
        openai_key = os.getenv("OPENAI_API_KEY")

        if openai_key:  # Use ChatGPT API
            headers = {"Authorization": f"Bearer {openai_key}"}
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": user_input}],
            }
            r = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
            )
            answer = r.json()["choices"][0]["message"]["content"]
            return jsonify({"answer": answer})

        elif hf_token:  # Use Hugging Face Inference API
            headers = {"Authorization": f"Bearer {hf_token}"}
            r = requests.post(
                "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill",
                headers=headers,
                json={"inputs": user_input},
            )
            answer = r.json()[0]["generated_text"]
            return jsonify({"answer": answer})

        else:  # Fallback: rule-based
            return jsonify(
                {"answer": "AI insights are disabled. Please set OPENAI_API_KEY or HF_TOKEN."}
            )

    except Exception as e:
        return jsonify({"answer": f"Error: {str(e)}"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
