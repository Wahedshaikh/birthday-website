from flask import Flask, render_template, request, redirect, session, url_for, flash
import sqlite3, json, os
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key")

DB = "birthday.db"

def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con


def setting(con, key, default=""):
    row = con.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    return row["value"] if row else default


def init_db():
    con = db()
    con.execute("""CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )""")
    con.execute("""CREATE TABLE IF NOT EXISTS balloons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT NOT NULL,
        voice TEXT NOT NULL
    )""")
    con.execute("""CREATE TABLE IF NOT EXISTS quiz (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        options TEXT NOT NULL,
        answer TEXT NOT NULL
    )""")
    defaults = {
        "friend_name": "Ayesha",
        "nickname": "Aashu",
        "your_name": "Your Best Friend",
        "welcome": "Happy Birthday, Aashu! 🎂💕",
        "intro": "Aaj ka din meri favourite girl ke naam hai. Ready ho ek chhote se surprise ke liye? ✨",
        "sweet1": "Aashu, pata nahi humari friendship kab itni special ban gayi, but ab tu meri life ka bohot important part hai. ❤️",
        "sweet2": "Tere saath choti choti baatein bhi special memories ban jaati hain. Thank you for always being you. 🫂",
        "sweet3": "Bas aise hi hamesha meri bestie rehna. Happy Birthday meri favourite person! 🎂💕",
        "bestie_question": "Kya hum best friend hai?",
        "admin_password": generate_password_hash("aashu123"),
    }

    for k, v in defaults.items():
        con.execute("INSERT OR IGNORE INTO settings(key,value) VALUES(?,?)", (k, v))

    if con.execute("SELECT COUNT(*) FROM balloons").fetchone()[0] == 0:
        balloons = [
            ("Aashu, tu meri favourite person hai 💕", "Aashu, tu meri favourite person hai!"),
            ("Thank you for always being there 🫂", "Thank you for always being there for me!"),
            ("Hamari friendship forever ♾️", "Hamari friendship forever!"),
            ("Aaj ka din sirf tumhare naam 🎂", "Aaj ka din sirf tumhare naam hai!"),
            ("Smile please, birthday girl! ✨", "Smile please, birthday girl!"),
        ]
        con.executemany("INSERT INTO balloons(text,voice) VALUES(?,?)", balloons)

    if con.execute("SELECT COUNT(*) FROM quiz").fetchone()[0] == 0:
        quizzes = [
            ("Meri favourite bestie kaun hai? 💕",
             ["Ayesha", "Someone else", "Mujhe nahi pata"], "Ayesha"),
            ("Humari friendship kaisi hai?",
             ["Temporary", "Forever ♾️", "Bas normal"], "Forever ♾️"),
            ("Birthday girl ko aaj kya milna chahiye?",
             ["Lots of happiness", "Cake 🎂", "Dono!"], "Dono!"),
        ]
        for q, opts, ans in quizzes:
            con.execute("INSERT INTO quiz(question,options,answer) VALUES(?,?,?)",
                        (q, json.dumps(opts), ans))

    con.commit()
    con.close()


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("admin"))
        return f(*args, **kwargs)
    return wrapper


@app.route("/")
def home():
    con = db()
    data = {k: setting(con, k) for k in
            ["friend_name", "nickname", "your_name", "welcome", "intro",
             "sweet1", "sweet2", "sweet3", "bestie_question"]}
    balloons = con.execute("SELECT * FROM balloons ORDER BY id").fetchall()
    quiz_rows = con.execute("SELECT * FROM quiz ORDER BY id").fetchall()
    quizzes = []
    for q in quiz_rows:
        quizzes.append({
            "id": q["id"],
            "question": q["question"],
            "options": json.loads(q["options"]),
            "answer": q["answer"]
        })
    con.close()
    return render_template("index.html", data=data, balloons=balloons, quizzes=quizzes)


@app.route("/admin", methods=["GET", "POST"])
def admin():
    con = db()

    if request.method == "POST" and request.form.get("action") == "login":
        password = request.form.get("password", "")
        saved = setting(con, "admin_password")
        if check_password_hash(saved, password):
            session["admin"] = True
            con.close()
            return redirect(url_for("admin"))
        flash("Wrong password ❤️ Try again.")

    if not session.get("admin"):
        con.close()
        return render_template("index.html", login_only=True)

    data = {k: setting(con, k) for k in
            ["friend_name", "nickname", "your_name", "welcome", "intro",
             "sweet1", "sweet2", "sweet3", "bestie_question"]}
    balloons = con.execute("SELECT * FROM balloons ORDER BY id").fetchall()
    quiz_rows = con.execute("SELECT * FROM quiz ORDER BY id").fetchall()
    quizzes = [{
        "id": q["id"], "question": q["question"],
        "options": json.loads(q["options"]), "answer": q["answer"]
    } for q in quiz_rows]
    con.close()

    return render_template("index.html", admin_page=True, data=data,
                           balloons=balloons, quizzes=quizzes)


@app.post("/admin/save-settings")
@admin_required
def save_settings():
    keys = ["friend_name", "nickname", "your_name", "welcome", "intro",
            "sweet1", "sweet2", "sweet3", "bestie_question"]
    con = db()
    for key in keys:
        con.execute("INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)",
                    (key, request.form.get(key, "").strip()))
    con.commit()
    con.close()
    flash("All main details saved globally ✨")
    return redirect(url_for("admin"))


@app.post("/admin/balloon")
@admin_required
def balloon():
    con = db()
    action = request.form.get("action")
    bid = request.form.get("id")
    if action == "delete":
        con.execute("DELETE FROM balloons WHERE id=?", (bid,))
    else:
        text = request.form.get("text", "").strip()
        if bid:
            con.execute("UPDATE balloons SET text=?,voice=? WHERE id=?", (text, text, bid))
        elif text:
            con.execute("INSERT INTO balloons(text,voice) VALUES(?,?)", (text, text))
    con.commit()
    con.close()
    return redirect(url_for("admin"))


@app.post("/admin/quiz")
@admin_required
def quiz():
    con = db()
    action = request.form.get("action")
    qid = request.form.get("id")
    if action == "delete":
        con.execute("DELETE FROM quiz WHERE id=?", (qid,))
    else:
        question = request.form.get("question", "").strip()
        options = [x.strip() for x in request.form.get("options", "").split("|") if x.strip()]
        answer = request.form.get("answer", "").strip()
        if qid:
            con.execute("UPDATE quiz SET question=?,options=?,answer=? WHERE id=?",
                        (question, json.dumps(options), answer, qid))
        elif question and options:
            con.execute("INSERT INTO quiz(question,options,answer) VALUES(?,?,?)",
                        (question, json.dumps(options), answer))
    con.commit()
    con.close()
    return redirect(url_for("admin"))


@app.post("/admin/password")
@admin_required
def change_password():
    new_password = request.form.get("new_password", "").strip()
    if new_password:
        con = db()
        con.execute("INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)",
                    ("admin_password", generate_password_hash(new_password)))
        con.commit()
        con.close()
        flash("Admin password changed 🔐")
    return redirect(url_for("admin"))


@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


init_db()

if __name__ == "__main__":
    app.run(debug=True)
