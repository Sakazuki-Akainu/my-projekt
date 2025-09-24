from flask import Flask, render_template, request
import pandas as pd
import plotly.express as px

app = Flask(__name__)

def generate_ai_insights(df):
    """Simple rule-based AI insights for any dataset"""
    insights = []
    try:
        insights.append(f"Dataset contains {df.shape[0]} rows and {df.shape[1]} columns.")
        numeric_cols = df.select_dtypes(include="number").columns.tolist()

        if numeric_cols:
            for col in numeric_cols[:3]:  # limit to 3 numeric cols for clarity
                insights.append(
                    f"📌 Column '{col}': mean = {df[col].mean():.2f}, min = {df[col].min()}, max = {df[col].max()}"
                )
            if len(numeric_cols) > 1:
                corr = df[numeric_cols].corr().iloc[0, 1]
                insights.append(f"🔗 Correlation between {numeric_cols[0]} and {numeric_cols[1]}: {corr:.2f}")
        else:
            insights.append("No numeric columns detected. Showing sample values instead:")
            for col in df.columns[:2]:
                insights.append(f"📌 Column '{col}': {df[col].unique()[:5]}")

    except Exception as e:
        insights.append(f"(AI failed to summarize: {e})")

    return " ".join(insights)

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file = request.files["file"]
        if file:
            df = pd.read_csv(file)

            # Table
            table_html = df.head().to_html(classes="table table-striped", index=False)

            # Graph (first 2 numeric cols only)
            numeric_cols = df.select_dtypes(include="number").columns
            if len(numeric_cols) >= 2:
                fig = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1], title="Scatter Plot")
            elif len(numeric_cols) == 1:
                fig = px.histogram(df, x=numeric_cols[0], title="Distribution")
            else:
                fig = px.histogram(df, x=df.columns[0], title="Counts")
            graph_html = fig.to_html(full_html=False)

            # Insights
            insights_text = generate_ai_insights(df)

            return render_template("upload.html", table=table_html, graph=graph_html, insights=insights_text)

    return render_template("upload.html", table=None, graph=None, insights=None)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
