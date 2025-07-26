import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import openai

# ─── CONFIGURATION ─────────────────────────────────────────────────────────────

app = Flask(__name__, static_folder="static")
CORS(app)

# Use an environment variable OPENAI_API_KEY for your key
openai.api_key = os.getenv("OPENAI_API_KEY", "")

# Simple SQLite DB for user data or logging if you need it
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///neonadsai.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# ─── ROUTES ────────────────────────────────────────────────────────────────────

@app.route("/api/generate-copy", methods=["POST"])
def generate_copy():
    data = request.get_json() or {}
    prompt_text = data.get("prompt", "").strip()
    n = data.get("num_variations", 3)

    if not prompt_text:
        return jsonify(error="`prompt` is required."), 400

    # Build a single prompt for GPT-3.5
    system_msg = {
        "role": "system",
        "content": (
            "أنت خبير في كتابة الإعلانات باللغة العربية والإنجليزية. "
            "أريدك أن تخرج لي {{n}} نسخٍ إعلانية احترافية قصيرة لكل منهما."
        ).replace("{{n}}", str(n))
    }
    user_msg = {
        "role": "user",
        "content": (
            "استخدم المعلومات التالية لكتابة إعلانين (عربي وإنجليزي) لكل نسخة:\n\n"
            f"{prompt_text}\n\n"
            "لكل نسخة، قدّم:\n"
            "- عنوان (Headline)\n"
            "- نص وجيز (Body)\n"
            "- نداء للعمل (Call to Action)\n"
            "- الفئة المستهدفة (Target Audience)\n\n"
            "رجاءً اعدّد النسخ وعدّد الحقول."
        )
    }

    try:
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[system_msg, user_msg],
            temperature=0.8,
            n=1
        )
        answer = resp.choices[0].message.content.strip()
        # Split by the marker "🚀" or numbered list
        variations = [v.strip() for v in answer.split("🚀") if v.strip()]
        return jsonify(variations=variations)
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify(status="ok"), 200

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    # Serve React build (put your built files into ./static)
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, "index.html")

# ─── STARTUP ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Create tables if needed
    db.create_all()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)

