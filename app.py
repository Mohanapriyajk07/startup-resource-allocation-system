import os
import csv
import io
from flask import Flask, request, jsonify, render_template

# Point Flask to the frontend folder for templates and static files
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

app = Flask(
    __name__,
    static_folder=os.path.join(FRONTEND_DIR, "static"),
    template_folder=os.path.join(FRONTEND_DIR, "templates"),
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # 2 MB limit

ALLOWED_EXTENSIONS = {"csv"}

# Scoring weights
WEIGHTS = {
    "impact": 0.35,
    "urgency": 0.30,
    "effort": 0.20,  # negative factor
    "cost": 0.15,    # negative factor
}

REQUIRED_COLUMNS = {"Project Name", "Impact Score", "Urgency Score", "Effort Score", "Cost Score"}


def allowed_file(filename: str) -> bool:
    """Check if the uploaded file has an allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_row(row: dict, row_index: int) -> list:
    """Validate a single CSV row and return a list of error messages (empty means OK)."""
    errors = []
    score_fields = ["Impact Score", "Urgency Score", "Effort Score", "Cost Score"]
    for field in score_fields:
        val = row.get(field, "").strip()
        if not val:
            errors.append(f"Row {row_index}: '{field}' is missing or empty.")
            continue
        try:
            num = float(val)
            if num < 1 or num > 5:
                errors.append(f"Row {row_index}: '{field}' must be between 1 and 5 (got {num}).")
        except ValueError:
            errors.append(f"Row {row_index}: '{field}' must be a number (got '{val}').")
    # Project Name check
    if not row.get("Project Name", "").strip():
        errors.append(f"Row {row_index}: 'Project Name' is missing or empty.")
    return errors


def calculate_priority_score(impact: float, urgency: float, effort: float, cost: float) -> float:
    """
    Calculate the weighted priority score.
    Effort and Cost are inverted (6 - value) so higher values penalize priority.
    """
    score = (
        impact * WEIGHTS["impact"]
        + urgency * WEIGHTS["urgency"]
        + (6 - effort) * WEIGHTS["effort"]
        + (6 - cost) * WEIGHTS["cost"]
    )
    return round(score, 2)


def get_priority_category(score: float) -> str:
    """Categorize priority based on score thresholds."""
    if score >= 3.8:
        return "High"
    elif score >= 2.8:
        return "Medium"
    else:
        return "Low"


def get_explanation(impact: float, urgency: float, effort: float, cost: float) -> str:
    """Generate a human-readable explanation tag for the ranking."""
    tags = []
    if impact >= 4:
        tags.append("High Impact")
    if urgency >= 4:
        tags.append("Urgent")
    if effort <= 2:
        tags.append("Low Effort")
    if cost <= 2:
        tags.append("Cost Efficient")
    if effort >= 4:
        tags.append("High Effort ⚠️")
    if cost >= 4:
        tags.append("Expensive ⚠️")
    return ", ".join(tags) if tags else "Balanced"


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    """Serve the main HTML page."""
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Accept a CSV upload, validate, score, rank, and return results as JSON.
    """
    # --- File presence check ---
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected. Please upload a CSV file."}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file format. Only .csv files are accepted."}), 400

    # --- Read and parse CSV ---
    try:
        stream = io.StringIO(file.stream.read().decode("utf-8-sig"))
        reader = csv.DictReader(stream)

        # Column validation
        if reader.fieldnames is None:
            return jsonify({"error": "The uploaded CSV file appears to be empty."}), 400

        # Strip whitespace from field names
        reader.fieldnames = [f.strip() for f in reader.fieldnames]
        missing = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing:
            return jsonify({
                "error": f"Missing required columns: {', '.join(sorted(missing))}. "
                         f"Required columns are: {', '.join(sorted(REQUIRED_COLUMNS))}."
            }), 400

        rows = list(reader)
        if not rows:
            return jsonify({"error": "The CSV file contains headers but no project data rows."}), 400

    except UnicodeDecodeError:
        return jsonify({"error": "Unable to read the file. Ensure it is a valid UTF-8 CSV."}), 400
    except csv.Error as e:
        return jsonify({"error": f"CSV parsing error: {str(e)}"}), 400

    # --- Validate rows ---
    all_errors = []
    for idx, row in enumerate(rows, start=2):  # start=2 because row 1 is headers
        row_errors = validate_row(row, idx)
        all_errors.extend(row_errors)

    if all_errors:
        return jsonify({"error": "Validation errors found:\n" + "\n".join(all_errors)}), 400

    # --- Score and rank ---
    results = []
    for row in rows:
        impact = float(row["Impact Score"].strip())
        urgency = float(row["Urgency Score"].strip())
        effort = float(row["Effort Score"].strip())
        cost = float(row["Cost Score"].strip())

        score = calculate_priority_score(impact, urgency, effort, cost)
        category = get_priority_category(score)
        explanation = get_explanation(impact, urgency, effort, cost)

        results.append({
            "project_name": row["Project Name"].strip(),
            "impact": impact,
            "urgency": urgency,
            "effort": effort,
            "cost": cost,
            "priority_score": score,
            "priority_category": category,
            "explanation": explanation,
        })

    # Sort descending by priority score
    results.sort(key=lambda x: x["priority_score"], reverse=True)

    # Add rank
    for rank, project in enumerate(results, start=1):
        project["rank"] = rank

    # Summary stats
    high = sum(1 for r in results if r["priority_category"] == "High")
    medium = sum(1 for r in results if r["priority_category"] == "Medium")
    low = sum(1 for r in results if r["priority_category"] == "Low")

    return jsonify({
        "success": True,
        "total_projects": len(results),
        "summary": {"high": high, "medium": medium, "low": low},
        "projects": results,
    })


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)
