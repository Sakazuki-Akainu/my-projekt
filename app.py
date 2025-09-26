from flask import Flask, render_template, request, jsonify
import pandas as pd
import plotly.express as px

app = Flask(__name__)
df = None  # store uploaded dataframe


@app.route("/")
def index():
    return render_template("upload.html")


@app.route("/upload", methods=["POST"])
def upload():
    global df
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    try:
        df = pd.read_csv(file)
        return jsonify({
            "columns": df.columns.tolist(),
            "rows": df.head(10).to_dict(orient="records")
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/graph", methods=["POST"])
def graph():
    global df
    if df is None:
        return jsonify({"error": "No data uploaded yet"}), 400

    try:
        data = request.get_json()
        x_col = data.get("x")
        y_col = data.get("y")
        chart_type = data.get("type")

        # ✅ convert to Python lists so JSON works
        x = df[x_col].astype(str).tolist()
        y = df[y_col].tolist()

        if chart_type == "line":
            fig = px.line(x=x, y=y, title=f"{y_col} vs {x_col}")
        elif chart_type == "bar":
            fig = px.bar(x=x, y=y, title=f"{y_col} vs {x_col}")
        elif chart_type == "scatter":
            fig = px.scatter(x=x, y=y, title=f"{y_col} vs {x_col}")
        elif chart_type == "pie":
            fig = px.pie(names=x, values=y, title=f"{y_col} distribution")
        else:
            return jsonify({"error": "Unknown chart type"}), 400

        return jsonify(fig.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json()
        question = data.get("question", "")

        # Dummy response for now (replace with real API like OpenAI later)
        answer = f"You asked: '{question}'. (This is a placeholder AI response.)"
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
