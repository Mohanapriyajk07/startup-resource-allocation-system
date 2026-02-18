# 🚀 Startup Resource Allocation System

A **decision-support web application** that helps startup managers decide which projects to fund first by removing guesswork and bias. It provides a clear, data-driven priority ranking using a weighted scoring model.

> **Note:** This is a decision-support tool, not automation. The final call always stays with the manager.

---

## 📋 Table of Contents

- [User Flow](#-user-flow)
- [Technology Stack](#-technology-stack)
- [Input Data Format](#-input-data-format)
- [Priority Scoring Logic](#-priority-scoring-logic)
- [Project Structure](#-project-structure)
- [Setup & Run](#-setup--run)
- [Testing](#-testing)
- [Error Handling](#-error-handling)

---

## 🔄 User Flow

1. **Open the web app** → Navigate to `http://localhost:5000`
2. **Upload a CSV file** → Drag-and-drop or browse for your project data file
3. **Click "Analyze Projects"** → The app processes and scores all projects
4. **View Results** → The app displays:
   - **Summary Cards** — Total projects, High / Medium / Low counts
   - **Priority Distribution Bar** — Visual breakdown of priority categories
   - **Ranked Project Table** — Sorted list with scores, categories, and explanation tags

---

## 🛠 Technology Stack

| Layer      | Technology           | Why?                              |
|------------|----------------------|-----------------------------------|
| Frontend   | HTML + CSS + JS      | Fast to build, easy to explain    |
| Backend    | Python (Flask)       | Lightweight, perfect for APIs     |
| Data       | CSV file upload      | No database setup needed          |
| Logic      | Weighted scoring     | Transparent and auditable         |

---

## 📊 Input Data Format

The uploaded CSV **must** contain these columns:

| Column          | Type    | Range | Description                   |
|-----------------|---------|-------|-------------------------------|
| `Project Name`  | Text    | —     | Name of the project           |
| `Impact Score`  | Number  | 1–5   | Expected business impact      |
| `Urgency Score` | Number  | 1–5   | Time sensitivity              |
| `Effort Score`  | Number  | 1–5   | Implementation effort needed  |
| `Cost Score`    | Number  | 1–5   | Financial cost involved       |

Each row represents one project request.

**Example CSV:**
```csv
Project Name,Impact Score,Urgency Score,Effort Score,Cost Score
AI Chatbot Integration,5,4,3,2
Mobile App Redesign,4,5,4,3
Security Audit,5,5,1,1
```

A sample file (`sample_projects.csv`) is included in the repository root.

---

## 🧮 Priority Scoring Logic

### Weights

| Factor   | Weight | Direction | Reasoning                                    |
|----------|--------|-----------|----------------------------------------------|
| Impact   | 0.35   | Positive  | Highest importance — business value           |
| Urgency  | 0.30   | Positive  | Important — time-sensitive projects first     |
| Effort   | 0.20   | Negative  | High effort projects are penalized            |
| Cost     | 0.15   | Negative  | High cost projects are penalized              |

### Formula

```
Priority Score = (Impact × 0.35)
               + (Urgency × 0.30)
               + ((6 - Effort) × 0.20)    ← inverted
               + ((6 - Cost) × 0.15)      ← inverted
```

**Why invert Effort and Cost?**
- A project with Effort = 5 (very hard) should score **lower**, not higher
- `(6 - 5) = 1` → contributes minimally to the score
- `(6 - 1) = 5` → contributes maximally to the score

### Score Range: **1.0 – 5.0**

### Priority Categories

| Category    | Score Range | Meaning                          |
|-------------|-------------|----------------------------------|
| 🟢 **High** | ≥ 3.8       | Fund immediately                |
| 🟡 **Medium** | 2.8 – 3.79 | Consider with available budget  |
| 🔴 **Low**  | < 2.8       | Defer or reconsider             |

### Explanation Tags

Each project also receives auto-generated explanation tags:
- **High Impact** — Impact ≥ 4
- **Urgent** — Urgency ≥ 4
- **Low Effort** — Effort ≤ 2
- **Cost Efficient** — Cost ≤ 2
- **High Effort ⚠️** — Effort ≥ 4
- **Expensive ⚠️** — Cost ≥ 4

---

## 📁 Project Structure

```
Starup allocationsysytem/
├── backend/                    # ← Backend (Flask API)
│   ├── app.py                  #    Main Flask application & scoring logic
│   ├── requirements.txt        #    Python dependencies
│   └── uploads/                #    (auto-created) temporary upload folder
├── frontend/                   # ← Frontend (HTML/CSS/JS)
│   ├── templates/
│   │   └── index.html          #    Main HTML page
│   └── static/
│       ├── style.css           #    Premium dark-themed stylesheet
│       └── script.js           #    Client-side logic & rendering
├── sample_projects.csv         # Sample input data for testing
└── README.md                   # Project documentation
```

---

## ⚙️ Setup & Run

### Prerequisites
- Python 3.8+
- pip
- Flask (`pip install flask`)

### Commands

**Start the backend (serves both backend API + frontend):**
```bash
cd backend
python app.py
```

Then open **http://localhost:5000** in your browser.

> Flask serves the frontend files (HTML/CSS/JS) automatically from the `frontend/` folder. No separate frontend server is needed.

---

## 🧪 Testing

Use the included `sample_projects.csv` or create your own. Test scenarios:

| Scenario                          | Expected Outcome                           |
|-----------------------------------|--------------------------------------------|
| High Impact + High Urgency        | Should rank at the top (High priority)     |
| High Cost + High Effort           | Should rank lower (penalized)              |
| Low Effort + Cost Efficient       | Should boost ranking                       |
| Mixed scores                      | Should fall in Medium priority range       |
| Invalid file (e.g., `.txt`)       | Error message: invalid format              |
| Missing columns                   | Error message listing missing columns      |
| Empty CSV (only headers)          | Error message: no data rows                |
| Scores outside 1–5 range          | Error message with specific row number     |

---

## 🛡 Error Handling

Basic validation is implemented to ensure reliability:

- **Wrong file format** → Only `.csv` files accepted
- **Missing columns** → Clear error listing which columns are missing
- **Empty file** → Detected and reported
- **Invalid score values** → Must be numbers between 1 and 5
- **Row-level errors** → Reported with specific row numbers
- **File size limit** → Maximum 2 MB upload size
- **Network errors** → Graceful error display on the frontend

---

## 📜 License

This project is for educational and demonstration purposes.
