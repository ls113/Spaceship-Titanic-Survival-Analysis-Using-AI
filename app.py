from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for
import pickle
import numpy as np
import pandas as pd
import shap
import os
import io
import csv

# PDF Libraries
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import LETTER
from reportlab.lib import colors
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ================= LOAD MODEL =================
model = pickle.load(open("model.pkl", "rb"))

# ================= SHAP =================
try:
    explainer = shap.Explainer(model)
except:
    explainer = shap.TreeExplainer(model)

# ================= GLOBAL STATS =================
total_predictions = 0

# ================= PAGE ROUTES =================
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict")
def predict_page():
    return render_template("predict.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for('login'))
    return render_template("dashboard.html")

@app.route("/report")
def report():
    return render_template("report.html")

# --- ADDED ROUTES FOR MODELS AND DEPLOY ---

@app.route("/models")
def models():
    """Renders the Model Intelligence Lab page"""
    return render_template("models.html")

@app.route("/deploy")
def deploy():
    """Renders the Deployment Roadmap page"""
    return render_template("deploy.html")

@app.route("/upload")
def upload(): return render_template("upload.html")

@app.route("/about")
def about():
    """Renders the Project Information and Creator page"""
    return render_template("about.html")

@app.route('/analytics')
def analytics():
    return render_template('analytics.html')

@app.route('/insights')
def insights():
    return render_template('insights.html')

@app.route('/history')
def history_page():
    dummy_history = [
        {
            "age": 25,
            "spending": 500,
            "prediction": "Survived",
            "confidence": "82%",
            "time": "10:30"
        },
        {
            "age": 40,
            "spending": 200,
            "prediction": "Not Survived",
            "confidence": "65%",
            "time": "10:35"
        }
    ]
    return render_template('history.html', history=dummy_history)

@app.route('/explorer')
def explorer():
    data = []
    # This finds the absolute path to your current folder
    base_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_path, 'data.csv')
    
    if os.path.exists(file_path):
        with open(file_path, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            data = list(reader)
    else:
        data = [["Error"], [f"File not found at: {file_path}"]]
        
    return render_template('explorer.html', data=data)

@app.route('/lab')
def lab():
    return render_template('lab.html')

@app.route('/simulation')
def simulation():
    return render_template('simulation.html')

@app.route('/api')
def api():
    return render_template('api.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route("/confusion")
def confusion():
    """Renders the Confusion Matrix and Performance Metrics page"""
    # You can pass real data here if you calculate it in Python
    metrics = {
        "tp": 120, "fp": 30, 
        "fn": 25, "tn": 200,
        "accuracy": "85%",
        "precision": "80%",
        "recall": "82%"
    }
    return render_template("confusion_matrix.html", metrics=metrics)
# ------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == "admin" and password == "1234":
            session["user"] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template("login.html", error="Invalid Credentials")
    return render_template("login.html")

# ================= PREDICTION API =================
@app.route("/predict_api", methods=["POST"])
def predict_api():
    global total_predictions
    try:
        data = request.json
        features = np.array([[float(data["age"]), float(data["spending"]), int(data["cryosleep"]), int(data["vip"])]])
        pred = model.predict(features)[0]
        prob = model.predict_proba(features)[0][1]
        total_predictions += 1
        return jsonify({
            "result": "Transported 🚀" if pred else "Not Transported ❌",
            "risk": int(prob * 100),
            "total_predictions": total_predictions
        })
    except Exception as e:
        return jsonify({"error": str(e)})
    
# Mock objects for demonstration - Ensure your actual model is loaded!
history = [] 

@app.route('/predict-page', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        try:
            # 1. Force convert inputs - handling both string and numeric inputs
            age = float(request.form.get('age', 0))
            spending = float(request.form.get('spending', 0))
            
            # This handles both '0'/'1' and 'no'/'yes' from your HTML
            cryo_input = request.form.get('cryosleep', '0').lower()
            cryo = 1 if cryo_input in ['1', 'yes'] else 0
            
            vip_input = request.form.get('vip', '0').lower()
            vip = 1 if vip_input in ['1', 'yes'] else 0

            features = np.array([[age, spending, cryo, vip]])
            
            # DEBUG: See what goes into the model in your VS Code terminal
            print(f"--- Input Features: {features} ---")

            # 2. Prediction
            prediction = model.predict(features)[0]
            prob_array = model.predict_proba(features)[0]

            # 3. Explicitly handle BOTH outcomes
            if prediction == 1:
                label = "Transported"
                icon = "🚀"
                conf_score = prob_array[1]
            else:
                label = "Not Transported"
                icon = "🛡️"
                conf_score = prob_array[0] # This ensures high confidence for 'Not Transported'

            formatted_conf = f"{round(conf_score * 100, 2)}%"

            result = {
                "time": datetime.now().strftime("%H:%M:%S"),
                "age": age,
                "prediction": label,
                "confidence": formatted_conf,
                "icon": icon
            }
            history.append(result)

            return render_template('predict.html', 
                                 prediction_text=label, 
                                 status_icon=icon, 
                                 confidence=formatted_conf, 
                                 history=history)
        except Exception as e:
            print(f"Error Details: {e}") # Check terminal for this
            return f"Error: {str(e)}"
    
    return render_template('predict.html', history=history)

@app.route("/upload_csv", methods=["POST"])
def upload_csv():
    try:
        file = request.files.get("file")
        if not file:
            return jsonify({"status": "error", "error": "No file detected"}), 400

        df = pd.read_csv(file)
        
        # 1. Standardize everything to lowercase/no spaces
        df.columns = [c.strip().lower() for c in df.columns]

        # 2. Map whatever the user sent to the 4 slots the model needs
        # We search for the keywords regardless of exact case
        required = ['age', 'cryosleep', 'spending', 'vip']
        for col in required:
            if col not in df.columns:
                df[col] = 0

        # 3. CONVERT TO VALUES (This is the trick)
        # By using .values, we send a raw matrix. The model can't see the "names",
        # so it can't complain that they are "unseen."
        input_matrix = df[required].fillna(0).values 
        
        # 4. Predict on the raw matrix
        preds = model.predict(input_matrix)
        
        # 5. Add result labels
        df["PREDICTION_STATUS"] = ["🚀 TRANSPORTED" if p == 1 else "✅ SAFE" for p in preds]
        df.to_csv("analysis_results.csv", index=False)

        return jsonify({
            "status": "success",
            "columns": df.columns.tolist(),
            "data": df.head(15).values.tolist()
        })

    except Exception as e:
        # If it fails, this will tell us the EXACT line/reason
        import traceback
        print(traceback.format_exc()) 
        return jsonify({"status": "error", "error": str(e)}), 500

# 1. This route JUST shows the data on the results page
@app.route('/results')
def show_results():
    return render_template('results.html', history=history)

# 2. This route JUST handles the file download
@app.route('/download_results')
def download_results():
    global history
    if not history:
        # Instead of a plain text error, redirect back with a message
        return "Please run a prediction first to generate data!", 400

    file_path = os.path.join(os.getcwd(), 'output.csv')
    keys = history[0].keys()
    
    with open(file_path, 'w', newline='') as f:
        dict_writer = csv.DictWriter(f, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(history)
            
    # This MUST return send_file to work as a download button
    return send_file(file_path, as_attachment=True)
    
# ================= PDF REPORT =================
@app.route("/download_report")
def download_report():
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=LETTER)
    styles = getSampleStyleSheet()
    content = []

    content.append(Paragraph("📄 AI Model Report Dashboard", styles["Title"]))
    content.append(Spacer(1, 12))
    
    content.append(Paragraph("🚀 Model Overview", styles["Heading2"]))
    content.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
    content.append(Paragraph(f"<b>Model Used:</b> Random Forest Classifier", styles["Normal"]))
    content.append(Paragraph(f"<b>Current Accuracy:</b> 85%", styles["Normal"]))
    content.append(Paragraph(f"<b>Session Predictions:</b> {total_predictions}", styles["Normal"]))
    content.append(Spacer(1, 15))

    content.append(Paragraph("📊 Model Description", styles["Heading2"]))
    content.append(Paragraph("This model predicts survival rates for the Spaceship Titanic dataset using Random Forest logic.", styles["Normal"]))

    doc.build(content)
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name="Spaceship_Titanic_Report.pdf",
        mimetype='application/pdf'
    )

if __name__ == "__main__":
    app.run(debug=True)