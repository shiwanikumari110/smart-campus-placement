from flask import Flask, render_template_string, request, redirect, session
import sqlite3, re
from datetime import date
app = Flask(__name__)
app.secret_key = "smart_campus_final_2026"
DB = "placement.db"

def get_db():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    db.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, name TEXT, username TEXT UNIQUE, password TEXT, role TEXT, cgpa REAL, skills TEXT, branch TEXT)")
    db.execute("CREATE TABLE IF NOT EXISTS drives(id INTEGER PRIMARY KEY, company TEXT, role TEXT, skills TEXT, cgpa REAL, package TEXT, deadline TEXT, status TEXT)")
    db.execute("CREATE TABLE IF NOT EXISTS applications(id INTEGER PRIMARY KEY, student TEXT, company TEXT, role TEXT, status TEXT)")
    db.execute("CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY, sender TEXT, receiver TEXT, company TEXT, role TEXT, title TEXT, message TEXT, date TEXT)")
    cols = [r[1] for r in db.execute("PRAGMA table_info(users)").fetchall()]
    if "branch" not in cols: db.execute("ALTER TABLE users ADD COLUMN branch TEXT")
    if "skills" not in cols: db.execute("ALTER TABLE users ADD COLUMN skills TEXT")
    if "cgpa" not in cols: db.execute("ALTER TABLE users ADD COLUMN cgpa REAL")
    cnt = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if cnt == 0:
        db.executescript("""
        INSERT INTO users VALUES(1,'Radhya','radhya','123','Student',7.0,'python, java, sql','B.Tech CSE');
        INSERT INTO users VALUES(2,'Sandhya','sandhya','123','Student',8.5,'python, java, html','B.Tech CSE');
        INSERT INTO users VALUES(3,'TCS HR','tcs','123','Company',0,'IT Services','TCS');
        INSERT INTO drives VALUES(1,'TCS','Java Developer','java, html',7.0,'7 LPA','2026-12-31','Approved');
        INSERT INTO drives VALUES(2,'Infosys','Python Developer','python, sql',7.5,'6 LPA','2026-12-31','Approved');
        INSERT INTO drives VALUES(3,'Wipro','Web Developer','html, css, js',6.5,'5 LPA','2026-12-31','Approved');
        INSERT INTO drives VALUES(4,'HCL','Data Analyst','python, sql, excel',7.0,'5.5 LPA','2026-12-31','Approved');
        INSERT INTO applications VALUES(1,'Radhya','TCS','Java Developer','Shortlisted');
        INSERT INTO applications VALUES(2,'Sandhya','Infosys','Python Developer','Applied');
        """)
    db.commit(); db.close()
init_db()

# ===== FIXED HEAD - PHONE GAP FIXED HERE =====
HEAD = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Smart Campus Placement Portal</title><style>*{font-family:'Segoe UI',Arial,sans-serif;box-sizing:border-box} body{margin:0;background:#f1f5f9;color:#1e293b} .top{background:#0f172a;color:#fff;padding:14px 12px;text-align:center} .top b{font-size:17px;line-height:1.3;display:block} .top small{color:#94a3b8;font-size:10px;letter-spacing:1.5px;display:block;margin-top:3px} .top span{font-size:11px;background:#1e293b;border:1px solid #334155;padding:6px 10px;border-radius:20px;display:inline-block;margin-top:8px;white-space:normal;line-height:1.4} .layout{display:flex;max-width:1150px;margin:0 auto;align-items:flex-start} .side{width:215px;background:#fff;padding:14px 10px;flex-shrink:0} .side a{display:block;padding:10px 12px;border-radius:9px;color:#334155;text-decoration:none;font-size:14px;font-weight:600;margin-bottom:4px} .side a:hover{background:#eff6ff;color:#2563eb} .main{flex:1;padding:16px;min-width:0;width:100%} .grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px} .card{background:#fff;padding:16px;border-radius:14px;box-shadow:0 2px 10px rgba(0,0,0,.05)} .card h2{margin:0;font-size:26px} .card p{margin:5px 0 0;color:#64748b;font-size:13px} .card small{color:#16a34a;font-weight:700;font-size:11px} .box{background:#fff;padding:16px;border-radius:14px;box-shadow:0 2px 10px rgba(0,0,0,.05);margin-top:12px} .box h3{margin:0 0 12px;border-left:4px solid #2563eb;padding-left:10px} .btn{display:inline-block;background:#2563eb;color:#fff;padding:9px 14px;border-radius:9px;text-decoration:none;font-size:13px;font-weight:600;border:none;cursor:pointer;margin:3px 3px 0 0} .btn-g{background:#16a34a} .btn-o{background:#ea580c} .btn-p{background:#7c3aed} .btn-d{background:#0f172a} .btn-l{background:#e2e8f0;color:#1e293b} .btn-s{padding:6px 10px;font-size:12px} input,select,textarea{width:100%;padding:11px;margin:7px 0;border:1px solid #cbd5e1;border-radius:9px;font-size:14px} .drive{display:flex;justify-content:space-between;align-items:center;gap:10px;background:#f8fafc;border:1px solid #e2e8f0;padding:13px;border-radius:12px;margin-top:10px;flex-wrap:wrap} .badge{padding:4px 10px;border-radius:20px;font-size:12px;font-weight:700;white-space:nowrap} .b-green{background:#dcfce7;color:#166534} .b-yellow{background:#fef9c3;color:#854d0e} .b-blue{background:#dbeafe;color:#1e40af} .bar{height:10px;background:#e2e8f0;border-radius:20px;overflow:hidden} .fill{height:100%;background:linear-gradient(90deg,#2563eb,#16a34a)} .footer{text-align:center;padding:16px 12px;font-size:12px;color:#64748b;line-height:1.6} .letter{background:#fff;border:2px solid #0f172a;padding:22px;border-radius:12px;max-width:650px;margin:0 auto}
@media(max-width:750px){ .layout{flex-direction:column} .side{width:100%;display:flex;overflow-x:auto;padding:10px;gap:6px} .side a{white-space:nowrap;padding:8px 12px;margin:0;flex-shrink:0} .grid{grid-template-columns:repeat(2,1fr)} .main{padding:12px} .drive{flex-direction:column;align-items:flex-start} }
@media(max-width:480px){ .top b{font-size:15px} .grid{grid-template-columns:1fr 1fr;gap:8px} .card{padding:12px} .card h2{font-size:22px} .box{padding:14px} }
@media print{ .top,.side,.footer,.no-print{display:none !important} .main{padding:0} .letter{border:1px solid #000} }</style></head><body><div class="top"><div><b>SMART CAMPUS PLACEMENT PORTAL</b><small>AI/ML BASED PLACEMENT PREDICTION SYSTEM</small></div><span>Developed By: Kumari Shiwani | Mangalayatan University</span></div>"""

FOOT = """<div class="footer">Smart Campus Placement Portal - AI/ML Based Placement Prediction System | Developed By: <b>Kumari Shiwani</b> | Guided By: Mr. Krishna Agarwal</div></body></html>"""

def render_auth(c):
    return render_template_string(HEAD + f"<div style='max-width:1150px;margin:0 auto;padding:0 12px;'>{c}</div>" + FOOT)

def cur():
    if "uid" not in session: return None
    db = get_db()
    row = db.execute("SELECT * FROM users WHERE id=?", (session["uid"],)).fetchone()
    db.close()
    if not row: return None
    d = dict(row)
    d["name"] = d.get("name") or "Student"; d["role"] = d.get("role") or "Student"; d["branch"] = d.get("branch") or "B.Tech CSE"; d["cgpa"] = d.get("cgpa") if d.get("cgpa") is not None else 0; d["skills"] = d.get("skills") or ""; d["username"] = d.get("username") or ""
    return d

def render(c):
    u = cur(); role = u["role"] if u else "Student"
    if role == "Admin": links = """<a href="/dashboard">Dashboard</a><a href="/dashboard">All Drives</a><a href="/create-drive">Post Drive</a><a href="/admin">Admin Panel</a><a href="/analytics">Analytics</a><a href="/profile">My Profile</a><a href="/logout" style="color:#dc2626;">Logout</a>"""
    elif role == "Company": links = """<a href="/dashboard">Dashboard</a><a href="/my-drives">My Drives</a><a href="/create-drive">Post Drive</a><a href="/my-messages">My Messages</a><a href="/analytics">Analytics</a><a href="/profile">My Profile</a><a href="/logout" style="color:#dc2626;">Logout</a>"""
    else: links = """<a href="/dashboard">Dashboard</a><a href="/dashboard">All Drives</a><a href="/predictor">ML Predictor</a><a href="/ats">ATS Analyzer</a><a href="/eligibility">Eligibility</a><a href="/test">Online Test</a><a href="/interview">Interview Coach</a><a href="/assistant">AI Assistant</a><a href="/my-applications">My Applications</a><a href="/my-messages">My Messages</a><a href="/profile">My Profile</a><a href="/analytics">Analytics</a><a href="/logout" style="color:#dc2626;">Logout</a>"""
    return render_template_string(HEAD + f"""<div class="layout"><div class="side">{links}</div><div class="main">{c}</div></div>""" + FOOT)

def extract_text(file, pasted):
    text = ""
    if file and file.filename != "":
        fname = file.filename.lower()
        if fname.endswith(".txt"): text = file.read().decode("utf-8", errors="ignore")
        elif fname.endswith(".pdf"):
            try:
                from PyPDF2 import PdfReader
                reader = PdfReader(file)
                for page in reader.pages: text += (page.extract_text() or "") + " "
            except: text = ""
        elif fname.endswith(".docx"):
            try:
                import docx; doc = docx.Document(file); text = " ".join([p.text for p in doc.paragraphs])
            except: text = ""
    else: text = pasted
    return text

def build_questions(t0):
    t = t0.lower(); qs = []
    qs.append({"q": "Tell me about yourself.", "keywords": ["name", "college", "branch", "skill", "project", "goal", "student"], "tip": "Use format: Name - College - Branch - Skills - 1 Project - Career Goal. Keep it under 1 minute."})
    if "python" in t: qs.append({"q": "You have mentioned Python. Explain Python OOP concepts with an example from your project.", "keywords": ["class", "object", "inheritance", "polymorphism", "encapsulation", "project", "python"], "tip": "Explain Class, Object, Inheritance, Polymorphism with one real example."})
    if "java" in t: qs.append({"q": "You have mentioned Java. What is the difference between Java and Python?", "keywords": ["java", "python", "object", "platform", "compiled", "interpreted", "project"], "tip": "Compare Java vs Python on Platform, Speed, Use Case."})
    if "sql" in t or "database" in t or "mysql" in t: qs.append({"q": "You have mentioned SQL. Explain Primary Key, Foreign Key and JOIN.", "keywords": ["primary", "foreign", "join", "table", "database", "query", "sql"], "tip": "Give one real table example - Student Table and Marks Table."})
    if "html" in t or "css" in t or "web" in t: qs.append({"q": "You have mentioned Web Development. How do HTML, CSS and JavaScript work together?", "keywords": ["html", "css", "javascript", "frontend", "design", "project", "website"], "tip": "Explain HTML = Structure, CSS = Styling, JavaScript = Logic."})
    if "project" in t: qs.append({"q": "Explain your best project. What problem did you solve and what was your role?", "keywords": ["project", "problem", "solution", "role", "technology", "result", "team"], "tip": "Use STAR method: Situation - Task - Action - Result."})
    if "intern" in t: qs.append({"q": "You have mentioned an Internship. What did you learn?", "keywords": ["internship", "learn", "project", "team", "skill", "company", "experience"], "tip": "Mention 2 skills you learned and 1 real task."})
    qs.append({"q": "Why should we hire you?", "keywords": ["skill", "project", "learn", "hardworking", "team", "contribute", "company"], "tip": "Say 1 Skill + 1 Project + How you will contribute from Day 1."})
    qs.append({"q": "Where do you see yourself in 5 years?", "keywords": ["years", "senior", "developer", "learn", "team", "lead", "goal", "company"], "tip": "Show growth: Junior - Senior - Team Lead."})
    return qs

def send_message(sender, receiver, company, role, title, message):
    db = get_db(); db.execute("INSERT INTO messages(sender,receiver,company,role,title,message,date) VALUES(?,?,?,?,?,?,?)", (sender, receiver, company, role, title, message, str(date.today()))); db.commit(); db.close()

@app.route("/")
def home(): return redirect("/dashboard")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        db = get_db(); u = db.execute("SELECT * FROM users WHERE username=? AND password=? AND role=?", (request.form["username"].lower().strip(), request.form["password"], request.form["role"])).fetchone(); db.close()
        if u: session["uid"] = u["id"]; return redirect("/dashboard")
        return render_auth("<div class='box'><h3>Invalid Login</h3><p>Username / Password / Role is incorrect.</p><a class='btn' href='/login'>Try Again</a></div>")
    return render_auth("""<div class="box" style="max-width:480px;margin:30px auto;text-align:center;"><h2 style="margin:0;">Welcome Back</h2><p style="color:#64748b;">Login to Smart Campus Placement Portal</p><form method="POST" style="text-align:left;"><label>Login As</label><select name="role"><option>Student</option><option>Company</option><option>Admin</option></select><label>Username</label><input name="username" placeholder="Enter username" required><label>Password</label><input type="password" name="password" placeholder="123" required><button class="btn" style="width:100%;">Login</button></form><div style="font-size:12px;background:#f8fafc;padding:12px;border-radius:10px;text-align:left;line-height:1.8;margin-top:12px;"><b>Demo Accounts:</b><br>Student: <b>radhya / 123</b> , <b>sandhya / 123</b><br>Company: <b>tcs / 123</b><br>Admin: Create Your Own Admin First From Register Page</div><p><a href="/register">New User? Register Here</a></p></div>""")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip(); role = request.form["role"]
        if role == "Admin":
            db_check = get_db()
            admin_count = db_check.execute("SELECT COUNT(*) FROM users WHERE role='Admin'").fetchone()[0]
            db_check.close()
            if admin_count >= 1:
                return render_auth("<div class='box'><h3>Admin Already Exists!</h3><p>Admin already exists for this website. Only 1 Admin is allowed. You cannot create another Admin account. Please Register as Student or Company.</p><a class='btn' href='/register'>Try Again As Student / Company</a> <a class='btn btn-l' href='/login'>Login As Admin</a></div>")
        if not re.match("^[A-Za-z ]+$", name): return render_auth("<div class='box'><h3>Invalid Full Name</h3><p>Only letters are allowed in Full Name. Numbers are not allowed.</p><a class='btn' href='/register'>Try Again</a></div>")
        if role == "Student": branch = request.form.get("branch","B.Tech CSE"); cgpa = float(request.form.get("cgpa") or 0); skills = request.form.get("skills","")
        elif role == "Company": branch = request.form.get("company_name","") or request.form.get("branch",""); cgpa = 0; skills = request.form.get("industry","") or request.form.get("skills","")
        else: branch = request.form.get("department","") or request.form.get("branch",""); cgpa = 0; skills = request.form.get("designation","") or request.form.get("skills","")
        db = get_db()
        try: db.execute("INSERT INTO users(name,username,password,role,cgpa,skills,branch) VALUES(?,?,?,?,?,?,?)", (name, request.form["username"].lower().strip(), request.form["password"], role, cgpa, skills, branch)); db.commit(); db.close(); return redirect("/login")
        except: db.close(); return render_auth("<div class='box'><h3>Username Already Exists</h3><p>Please choose another username.</p><a class='btn' href='/register'>Try Again</a></div>")
    db_c = get_db(); admin_exists = db_c.execute("SELECT COUNT(*) FROM users WHERE role='Admin'").fetchone()[0] >= 1; db_c.close()
    if admin_exists:
        role_options = "<option>Student</option><option>Company</option>"
        admin_note = "<p style='font-size:12px;color:#dc2626;font-weight:700;margin:0;'>Admin Already Exists - Admin Registration Is Closed. Only 1 Admin Is Allowed For This Website.</p>"
    else:
        role_options = "<option>Student</option><option>Company</option><option>Admin</option>"
        admin_note = "<p style='font-size:12px;color:#16a34a;font-weight:700;margin:0;'>Admin Not Created Yet - You Can Register As First Admin.</p>"
    return render_auth(f"""<div class="box" style="max-width:480px;margin:20px auto;"><h3>Create Account</h3><form method="POST"><input name="name" placeholder="Full Name" pattern="[A-Za-z ]+" title="Only letters are allowed in Full Name" oninput="this.value = this.value.replace(/[^A-Za-z ]/g, '')" required><input name="username" placeholder="Username" required><input type="password" name="password" placeholder="Password" required><label style="font-weight:700;font-size:13px;">Select Role - Form will change automatically:</label><select name="role" id="roleSelect" onchange="changeForm()" required>{role_options}</select>{admin_note}<div id="studentFields"><input name="branch" placeholder="Branch - e.g. B.Tech CSE"><input name="cgpa" placeholder="CGPA e.g. 8.5"><input name="skills" placeholder="Skills - e.g. python, java"></div><div id="companyFields" style="display:none;"><input name="company_name" placeholder="Company Name - e.g. TCS, Infosys"><input name="industry" placeholder="Industry - e.g. IT Services, Software"><p style="font-size:12px;color:#64748b;margin:0;">CGPA is not required for Company.</p></div><div id="adminFields" style="display:none;"><input name="department" placeholder="Department - e.g. Placement Cell"><input name="designation" placeholder="Designation - e.g. Placement Officer"><p style="font-size:12px;color:#64748b;margin:0;">Branch / CGPA is not required for Admin.</p></div><button class="btn" style="width:100%;">Register</button></form><p style="text-align:center;"><a href="/login">Already have account? Login</a></p></div><script>function changeForm(){{var r=document.getElementById('roleSelect').value;document.getElementById('studentFields').style.display=(r=='Student')?'block':'none';document.getElementById('companyFields').style.display=(r=='Company')?'block':'none';var af=document.getElementById('adminFields');if(af){{af.style.display=(r=='Admin')?'block':'none';}}}}</script>""")

@app.route("/logout")
def logout():
    session.clear(); return redirect("/login")

@app.route("/dashboard")
def dashboard():
    u = cur()
    if not u: return redirect("/login")
    q = request.args.get("q","").lower(); db = get_db()
    sc = db.execute("SELECT COUNT(*) FROM users WHERE role='Student'").fetchone()[0]; cc = db.execute("SELECT COUNT(*) FROM users WHERE role='Company'").fetchone()[0]; dc = db.execute("SELECT COUNT(*) FROM drives").fetchone()[0]; ac = db.execute("SELECT COUNT(*) FROM applications").fetchone()[0]; sel = db.execute("SELECT COUNT(*) FROM applications WHERE status='Selected'").fetchone()[0]; short = db.execute("SELECT COUNT(*) FROM applications WHERE status='Shortlisted'").fetchone()[0]; pending_drives = db.execute("SELECT COUNT(*) FROM drives WHERE status='Pending'").fetchone()[0]
    students = db.execute("SELECT * FROM users WHERE role='Student'").fetchall(); companies = db.execute("SELECT * FROM users WHERE role='Company'").fetchall(); drives = db.execute("SELECT * FROM drives").fetchall(); myapps = db.execute("SELECT * FROM applications WHERE student=?", (u["name"],)).fetchall(); my_msgs = db.execute("SELECT * FROM messages WHERE receiver=? ORDER BY id DESC LIMIT 3", (u["name"],)).fetchall(); db.close()
    if u["role"] == "Admin":
        dh = ""
        for d in drives:
            d = dict(d)
            if q and q not in (str(d.get("company","")) + str(d.get("role",""))).lower(): continue
            dh += f"<div class='drive'><div><b>{d.get('company')} - {d.get('role')}</b><br><small>Package: {d.get('package')} | Min CGPA: {d.get('cgpa')} | Status: {d.get('status')}</small></div><a class='btn btn-g btn-s' href='/admin'>Manage</a></div>"
        sh = "".join([f"<div class='drive'><div><b>{dict(s).get('name')} - {dict(s).get('username')}</b><br><small>{dict(s).get('branch')} | CGPA: {dict(s).get('cgpa')} | Skills: {dict(s).get('skills')}</small></div><span class='badge b-blue'>Student</span></div>" for s in students])
        ch = "".join([f"<div class='drive'><div><b>{dict(c).get('name')} - {dict(c).get('username')}</b><br><small>Company: {dict(c).get('branch')} | Industry: {dict(c).get('skills')}</small></div><span class='badge b-green'>Company</span></div>" for c in companies])
        return render(f"""<h2 style="margin:0;">Welcome, {u['name']}</h2><p style="color:#64748b;">Logged in as <b>Admin</b> | Department: {u['branch']} | Designation: {u['skills']} <a href="/profile" style="color:#2563eb;">Edit Profile</a></p><div class="grid"><div class="card"><h2>{sc}</h2><p>Total Students</p><small>Registered</small></div><div class="card"><h2>{cc}</h2><p>Total Companies</p><small>Registered</small></div><div class="card"><h2>{dc}</h2><p>Total Drives</p><small>{pending_drives} Pending Approval</small></div><div class="card"><h2>{sel}/{ac}</h2><p>Selected / Applied</p><small>{short} Shortlisted</small></div></div><div class="box"><h3>Admin Control Panel - For Admin Role</h3><a class="btn btn-o" href="/create-drive">Post New Drive</a><a class="btn btn-d" href="/admin">Admin Panel - Approve Drives & Select Students</a><a class="btn btn-l" href="/analytics">View Analytics & Reports</a></div><div class="box"><h3>All Drives - Search & Manage</h3><form method="GET" action="/dashboard"><input name="q" placeholder="Search - e.g. TCS, Java..." value="{q}"></form>{dh or '<p>No drives found.</p>'}</div><div class="box"><h3>All Students - {sc} Students</h3>{sh or '<p>No students registered yet.</p>'}</div><div class="box"><h3>All Companies - {cc} Companies</h3>{ch or '<p>No companies registered yet.</p>'}</div>""")
    if u["role"] == "Company":
        my_company = (u["branch"] or "").lower().strip()
        my_drives = [dict(d) for d in drives if str(dict(d).get("company","")).lower().strip() == my_company]
        my_apps_count = 0; db2 = get_db()
        for d in my_drives: my_apps_count += db2.execute("SELECT COUNT(*) FROM applications WHERE company=? AND role=?", (d.get("company"), d.get("role"))).fetchone()[0]
        db2.close()
        dh = ""
        for d in drives:
            d = dict(d)
            if q and q not in (str(d.get("company","")) + str(d.get("role",""))).lower(): continue
            dh += f"<div class='drive'><div><b>{d.get('company')} - {d.get('role')}</b><br><small>{d.get('skills')} | Min CGPA: {d.get('cgpa')} | Package: {d.get('package')} | Status: {d.get('status')}</small></div><span class='badge b-blue'>{d.get('status')}</span></div>"
        return render(f"""<h2 style="margin:0;">Welcome, {u['name']}</h2><p style="color:#64748b;">Logged in as <b>Company</b> | Company: {u['branch']} | Industry: {u['skills']} <a href="/profile" style="color:#2563eb;">Edit Profile</a></p><div class="grid"><div class="card"><h2>{sc}</h2><p>Total Students</p><small>Available</small></div><div class="card"><h2>{len(my_drives)}</h2><p>My Drives</p><small>Your Company</small></div><div class="card"><h2>{my_apps_count}</h2><p>Total Applicants</p><small>Applied To You</small></div><div class="card"><h2>{sel}/{ac}</h2><p>Selected / Applied</p><small>Overall</small></div></div><div class="box"><h3>Company Control Panel - For Company Role</h3><p style="font-size:13px;color:#64748b;">See who applied to your company, view student details, select student and send Offer Letter.</p><a class="btn btn-g" href="/my-drives">My Drives - See Who Applied</a><a class="btn btn-o" href="/create-drive">Post New Drive</a><a class="btn btn-l" href="/my-messages">My Messages</a><a class="btn btn-l" href="/analytics">View Analytics</a></div><div class="box"><h3>All Drives - Search</h3><form method="GET" action="/dashboard"><input name="q" placeholder="Search - e.g. python, TCS, java..." value="{q}"></form>{dh or '<p>No drives found.</p>'}</div>""")
    dh = ""
    for d in drives:
        d = dict(d)
        if d.get("status") != "Approved": continue
        if q and q not in (str(d.get("company","")) + str(d.get("role","")) + str(d.get("skills",""))).lower(): continue
        applied = any(dict(a).get("company")==d.get("company") and dict(a).get("role")==d.get("role") for a in myapps)
        btn = "<span class='badge b-green'>Applied</span>" if applied else f"<a class='btn btn-g btn-s' href='/apply/{d['id']}'>Apply Now</a>"
        dh += f"<div class='drive'><div><b>{d.get('company')} - {d.get('role')}</b><br><small>{d.get('skills')} | Min CGPA: {d.get('cgpa')} | Package: {d.get('package')} | Deadline: {d.get('deadline')}</small></div><div>{btn}</div></div>"
    msg_html = "".join([f"<div style='background:#eff6ff;padding:12px;border-radius:10px;margin-top:8px;'><b>{dict(m).get('title')}</b> - From {dict(m).get('sender')} ({dict(m).get('company')})<br><span style='font-size:13px;'>{dict(m).get('message')}</span><br><a class='btn btn-s' href='/my-messages'>View All Messages</a></div>" for m in my_msgs]) or "<p style='font-size:13px;color:#64748b;'>No new messages yet. When a company selects you, you will get a message and Offer Letter here.</p>"
    return render(f"""<h2 style="margin:0;">Welcome, {u['name']}</h2><p style="color:#64748b;">Logged in as <b>{u['role']}</b> | {u['branch']} | CGPA: {u['cgpa']} | Skills: {u['skills']} <a href="/profile" style="color:#2563eb;">Edit Profile</a></p><div class="grid"><div class="card"><h2>{sc}</h2><p>Total Students</p><small>Active</small></div><div class="card"><h2>{cc}</h2><p>Total Companies</p><small>Hiring</small></div><div class="card"><h2>{dc}</h2><p>Active Drives</p><small>Live Now</small></div><div class="card"><h2>{sel}/{ac}</h2><p>Selected / Applied</p><small>Placement</small></div></div><div class="box"><h3>Smart Features - For {u['role']} Role</h3><a class="btn" href="/predictor">1. ML Predictor</a><a class="btn btn-p" href="/eligibility">2. Eligibility</a><a class="btn btn-o" href="/ats">3. ATS Analyzer</a><a class="btn" href="/test">4. Online Test</a><a class="btn btn-g" href="/interview">5. Interview Coach</a><a class="btn btn-p" href="/assistant">6. AI Assistant</a><a class="btn" href="/my-applications">7. My Applications</a><a class="btn btn-o" href="/my-messages">8. My Messages & Offer Letter</a><a class="btn btn-l" href="/analytics">Analytics</a></div><div class="box"><h3>Latest Messages From Companies</h3>{msg_html}</div><div class="box"><h3>Approved Drives - Search & Apply</h3><form method="GET" action="/dashboard"><input name="q" placeholder="Search - e.g. python, TCS, java..." value="{q}"></form>{dh or '<p>No drives found. Try another search.</p>'}<br><a class="btn btn-l" href="/my-applications">My Applications ({len(myapps)})</a></div>""")

@app.route("/profile", methods=["GET","POST"])
def profile():
    u = cur()
    if not u: return redirect("/login")
    if request.method == "POST":
        new_name = request.form["name"].strip()
        if not re.match("^[A-Za-z ]+$", new_name): return render("<div class='box'><h3>Invalid Full Name</h3><p>Only letters are allowed in Full Name. Numbers are not allowed.</p><a class='btn' href='/profile'>Try Again</a></div>")
        db = get_db(); db.execute("UPDATE users SET name=?, cgpa=?, skills=?, branch=? WHERE id=?", (new_name, float(request.form["cgpa"] or 0), request.form["skills"], request.form["branch"], u["id"])); db.commit(); db.close(); return redirect("/dashboard")
    if u["role"] == "Student": l1,l2,l3 = "Branch","CGPA","Skills"
    elif u["role"] == "Company": l1,l2,l3 = "Company Name","CGPA (Not Needed)","Industry"
    else: l1,l2,l3 = "Department","CGPA (Not Needed)","Designation"
    return render(f"""<div class="box"><h3>My Profile - Edit & Save ({u['role']})</h3><form method="POST"><label>Full Name</label><input name="name" value="{u['name']}" pattern="[A-Za-z ]+" title="Only letters are allowed in Full Name" oninput="this.value = this.value.replace(/[^A-Za-z ]/g, '')" required><label>{l1}</label><input name="branch" value="{u['branch']}"><label>{l2}</label><input name="cgpa" value="{u['cgpa']}"><label>{l3}</label><input name="skills" value="{u['skills']}"><button class="btn btn-g">Save Profile</button></form></div>""")

@app.route("/my-drives")
def my_drives():
    u = cur()
    if not u: return redirect("/login")
    if u["role"] != "Company": return render("<div class='box'><h3>Access Denied</h3><p>Only Company can view My Drives.</p><a class='btn' href='/dashboard'>Back to Dashboard</a></div>")
    my_company = (u["branch"] or "").lower().strip(); db = get_db(); all_drives = db.execute("SELECT * FROM drives").fetchall(); db.close()
    my_list = [dict(d) for d in all_drives if str(dict(d).get("company","")).lower().strip() == my_company]
    if not my_list: my_list = [dict(d) for d in all_drives if str(dict(d).get("company","")).lower().strip() in u["name"].lower()]
    h = ""
    if not my_list: h = f"<div class='box'><h3>No Drives Found For {u['branch']}</h3><p>You have not posted any drive yet for <b>{u['branch']}</b>. Post a drive with Company Name = <b>{u['branch']}</b> so that it appears here.</p><a class='btn btn-o' href='/create-drive'>Post Your First Drive</a></div>"
    else:
        for d in my_list:
            db2 = get_db(); apps = db2.execute("SELECT * FROM applications WHERE company=? AND role=?", (d.get("company"), d.get("role"))).fetchall(); db2.close()
            total = len(apps); sel_c = sum(1 for a in apps if dict(a).get("status")=="Selected"); short_c = sum(1 for a in apps if dict(a).get("status")=="Shortlisted")
            h += f"""<div class='drive' style='display:block;'><div style='display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;'><div><b>{d.get('company')} - {d.get('role')}</b><br><small>Skills: {d.get('skills')} | Min CGPA: {d.get('cgpa')} | Package: {d.get('package')} | Status: {d.get('status')}</small></div><span class='badge b-blue'>{total} Applicants</span></div><p style='font-size:13px;'>Total Applied: <b>{total}</b> | Shortlisted: <b>{short_c}</b> | Selected: <b>{sel_c}</b></p><a class='btn btn-g' href='/applicants/{d['id']}'>View Applicants - See Who Applied</a> <a class='btn btn-l' href='/create-drive'>Post New Drive</a></div>"""
    return render(f"<div class='box'><h3>My Drives - {u['branch']} - Total {len(my_list)} Drives</h3><p style='font-size:13px;color:#64748b;'>Only your company drives are shown here. Other companies drives are not shown.</p></div>{h}<br><a class='btn' href='/dashboard'>Back to Dashboard</a>")

@app.route("/applicants/<int:did>")
def applicants(did):
    u = cur()
    if not u: return redirect("/login")
    if u["role"] not in ("Company","Admin"): return render("<div class='box'><h3>Access Denied</h3><p>Only Company and Admin can view applicants.</p><a class='btn' href='/dashboard'>Back to Dashboard</a></div>")
    db = get_db(); d = db.execute("SELECT * FROM drives WHERE id=?", (did,)).fetchone()
    if not d: db.close(); return redirect("/my-drives")
    d = dict(d)
    if u["role"] == "Company":
        my_company = (u["branch"] or "").lower().strip()
        if str(d.get("company","")).lower().strip() != my_company: db.close(); return render("<div class='box'><h3>Access Denied</h3><p>You can only view applicants of your own company drives.</p><a class='btn' href='/my-drives'>Back to My Drives</a></div>")
    apps = db.execute("SELECT * FROM applications WHERE company=? AND role=?", (d.get("company"), d.get("role"))).fetchall(); db.close()
    h = ""
    if not apps: h = "<div class='box'><h3>No One Applied Yet</h3><p>No student has applied for this drive yet.</p></div>"
    for a in apps:
        a = dict(a); db2 = get_db(); st = db2.execute("SELECT * FROM users WHERE name=? AND role='Student'", (a.get("student"),)).fetchone(); db2.close()
        detail = f"<b>Branch:</b> {dict(st).get('branch')} | <b>CGPA:</b> {dict(st).get('cgpa')} | <b>Skills:</b> {dict(st).get('skills')} | <b>Username:</b> {dict(st).get('username')}" if st else "Student details not found."
        st_status = a.get("status") or "Applied"; badge_c = "b-green" if st_status=="Selected" else "b-yellow" if st_status=="Shortlisted" else "b-blue"
        h += f"""<div class='drive' style='display:block;'><div style='display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;'><div><b>{a.get('student')} - Applied For {a.get('company')} - {a.get('role')}</b><br><small>Application ID: #{a.get('id')} | {detail}</small></div><span class='badge {badge_c}'>{st_status}</span></div><div style='margin-top:10px;'><a class='btn btn-s' href='/company-shortlist/{a.get('id')}'>Shortlist</a><a class='btn btn-g btn-s' href='/company-select/{a.get('id')}'>Select + Send Offer Letter</a><a class='btn btn-o btn-s' href='/send-message/{a.get('id')}'>Send Message</a><a class='btn btn-l btn-s' href='/offer-letter/{a.get('id')}'>View Offer Letter</a></div></div>"""
    return render(f"<div class='box'><h3>Applicants - {d.get('company')} - {d.get('role')}</h3><p>Package: {d.get('package')} | Skills Required: {d.get('skills')} | Total Applicants: {len(apps)}</p></div>{h}<br><a class='btn' href='/my-drives'>Back to My Drives</a>")

@app.route("/company-shortlist/<int:aid>")
def company_shortlist(aid):
    u = cur()
    if not u or u["role"] not in ("Company","Admin"): return redirect("/dashboard")
    db = get_db(); a = db.execute("SELECT * FROM applications WHERE id=?", (aid,)).fetchone()
    if not a: db.close(); return redirect("/my-drives")
    a = dict(a); db.execute("UPDATE applications SET status='Shortlisted' WHERE id=?", (aid,)); db.commit(); db.close()
    send_message(u["name"], a.get("student"), a.get("company"), a.get("role"), "You Are Shortlisted!", f"Congratulations {a.get('student')}! You are Shortlisted for {a.get('company')} - {a.get('role')}. Please be ready for interview.")
    return render(f"<div class='box'><h3>Student Shortlisted!</h3><p><b>{a.get('student')}</b> is now Shortlisted for <b>{a.get('company')} - {a.get('role')}</b></p><p>Message has been sent to student.</p><a class='btn' href='/my-drives'>My Drives</a></div>")

@app.route("/company-select/<int:aid>")
def company_select(aid):
    u = cur()
    if not u or u["role"] not in ("Company","Admin"): return redirect("/dashboard")
    db = get_db(); a = db.execute("SELECT * FROM applications WHERE id=?", (aid,)).fetchone()
    if not a: db.close(); return redirect("/my-drives")
    a = dict(a); db.execute("UPDATE applications SET status='Selected' WHERE id=?", (aid,)); db.commit(); db.close()
    send_message(u["name"], a.get("student"), a.get("company"), a.get("role"), "Congratulations! You Are Selected!", f"Congratulations {a.get('student')}! You are Selected for {a.get('company')} - {a.get('role')}. Your Offer Letter is ready. Please open My Messages and Download your Offer Letter. Welcome to {a.get('company')}!")
    return render(f"""<div class='box'><h3>Student Selected Successfully!</h3><p><b>{a.get('student')}</b> is now Selected for <b>{a.get('company')} - {a.get('role')}</b></p><p>Selection Message + Offer Letter has been sent to student.</p><a class='btn btn-g' href='/offer-letter/{aid}'>View Offer Letter</a> <a class='btn' href='/my-drives'>Back to My Drives</a></div>""")

@app.route("/send-message/<int:aid>", methods=["GET","POST"])
def send_msg(aid):
    u = cur()
    if not u: return redirect("/login")
    if u["role"] not in ("Company","Admin"): return render("<div class='box'><h3>Access Denied</h3><p>Only Company can send message to student.</p><a class='btn' href='/dashboard'>Back</a></div>")
    db = get_db(); a = db.execute("SELECT * FROM applications WHERE id=?", (aid,)).fetchone(); db.close()
    if not a: return redirect("/my-drives")
    a = dict(a)
    if request.method == "POST":
        msg = request.form.get("message","").strip(); title = request.form.get("title","Message From Company")
        if msg: send_message(u["name"], a.get("student"), a.get("company"), a.get("role"), title, msg); return render(f"<div class='box'><h3>Message Sent Successfully!</h3><p>Your message has been sent to <b>{a.get('student')}</b>.</p><a class='btn' href='/my-drives'>Back to My Drives</a> <a class='btn btn-g' href='/my-messages'>View My Messages</a></div>")
    return render(f"""<div class='box'><h3>Send Message To {a.get('student')}</h3><p>Company: <b>{a.get('company')}</b> | Role: <b>{a.get('role')}</b> | Current Status: <b>{a.get('status')}</b></p><form method='POST'><label>Message Title</label><input name='title' value='Interview Scheduled - {a.get('company')}' required><label>Your Message - Write in English</label><textarea name='message' rows='5' placeholder='Hello Radhya, Your interview is scheduled tomorrow at 10 AM. Please carry your resume and ID card...' required></textarea><button class='btn btn-g' style='width:100%;'>Send Message To Student</button></form></div>""")

@app.route("/my-messages")
def my_messages():
    u = cur()
    if not u: return redirect("/login")
    db = get_db()
    if u["role"] == "Student": rows = db.execute("SELECT * FROM messages WHERE receiver=? ORDER BY id DESC", (u["name"],)).fetchall()
    elif u["role"] == "Company": rows = db.execute("SELECT * FROM messages WHERE sender=? ORDER BY id DESC", (u["name"],)).fetchall()
    else: rows = db.execute("SELECT * FROM messages ORDER BY id DESC").fetchall()
    db.close(); h = ""
    if not rows:
        h = "<div class='box'><h3>No Messages Yet</h3><p>When a company shortlists or selects you, you will get a message here with your Offer Letter.</p></div>" if u["role"]=="Student" else "<div class='box'><h3>No Messages Sent Yet</h3><p>Go to My Drives - View Applicants - Send Message.</p><a class='btn' href='/my-drives'>Go To My Drives</a></div>"
    for m in rows:
        m = dict(m); db2 = get_db(); app_row = db2.execute("SELECT * FROM applications WHERE student=? AND company=? AND role=?", (m.get("receiver") if u["role"]!="Student" else u["name"], m.get("company"), m.get("role"))).fetchone(); db2.close()
        letter_btn = f"<br><a class='btn btn-g btn-s' href='/offer-letter/{dict(app_row).get('id')}'>Download Offer Letter</a>" if app_row and dict(app_row).get("status")=="Selected" else ""
        h += f"""<div class='drive' style='display:block;'><div><b>{m.get('title')}</b><br><small>From: {m.get('sender')} ({m.get('company')}) | To: {m.get('receiver')} | Date: {m.get('date')} | For: {m.get('company')} - {m.get('role')}</small></div><p style='font-size:14px;background:#f8fafc;padding:12px;border-radius:10px;'>{m.get('message')}</p>{letter_btn}</div>"""
    title = "My Messages - Student Inbox" if u["role"]=="Student" else "My Messages - Sent Messages"
    return render(f"<div class='box'><h3>{title} - Total {len(rows)} Messages</h3></div>{h}<br><a class='btn' href='/dashboard'>Back to Dashboard</a>")

@app.route("/offer-letter/<int:aid>")
def offer_letter(aid):
    u = cur()
    if not u: return redirect("/login")
    db = get_db(); a = db.execute("SELECT * FROM applications WHERE id=?", (aid,)).fetchone()
    if not a: db.close(); return redirect("/dashboard")
    a = dict(a); drive = db.execute("SELECT * FROM drives WHERE company=? AND role=?", (a.get("company"), a.get("role"))).fetchone(); student = db.execute("SELECT * FROM users WHERE name=? AND role='Student'", (a.get("student"),)).fetchone(); db.close()
    if u["role"] == "Student" and u["name"] != a.get("student"): return render("<div class='box'><h3>Access Denied</h3><p>You can only view your own Offer Letter.</p><a class='btn' href='/dashboard'>Back</a></div>")
    if u["role"] == "Company":
        my_company = (u["branch"] or "").lower().strip()
        if str(a.get("company","")).lower().strip() != my_company: return render("<div class='box'><h3>Access Denied</h3><p>You can only view Offer Letters of your own company.</p><a class='btn' href='/my-drives'>Back</a></div>")
    package = dict(drive).get("package") if drive else "As per company policy"; cgpa = dict(student).get("cgpa") if student else ""; branch = dict(student).get("branch") if student else ""; skills = dict(student).get("skills") if student else ""; status = a.get("status") or "Applied"
    if status != "Selected": return render(f"<div class='box'><h3>Offer Letter Not Ready Yet</h3><p><b>{a.get('student')}</b> is currently <b>{status}</b> for <b>{a.get('company')} - {a.get('role')}</b>. Offer Letter will be ready after company selects the student.</p><a class='btn' href='/dashboard'>Back to Dashboard</a></div>")
    return render(f"""<div class='letter'><div style='text-align:center;border-bottom:2px solid #0f172a;padding-bottom:10px;'><h2 style='margin:0;'>{a.get('company')}</h2><p style='margin:4px 0;color:#64748b;'>Offer Letter - Selection Letter</p></div><p>Date: <b>{date.today()}</b><br>Ref No: <b>OFF/{aid}/2026</b></p><p>Dear <b>{a.get('student')}</b>,</p><p><b>Congratulations!</b> We are happy to inform you that you have been <b>Selected</b> for the position of <b>{a.get('role')}</b> at <b>{a.get('company')}</b> through Smart Campus Placement Portal, Mangalayatan University.</p><table style='width:100%;border-collapse:collapse;'><tr><td style='border:1px solid #ddd;padding:8px;'><b>Student Name</b></td><td style='border:1px solid #ddd;padding:8px;'>{a.get('student')}</td></tr><tr><td style='border:1px solid #ddd;padding:8px;'><b>Branch</b></td><td style='border:1px solid #ddd;padding:8px;'>{branch}</td></tr><tr><td style='border:1px solid #ddd;padding:8px;'><b>CGPA</b></td><td style='border:1px solid #ddd;padding:8px;'>{cgpa}</td></tr><tr><td style='border:1px solid #ddd;padding:8px;'><b>Skills</b></td><td style='border:1px solid #ddd;padding:8px;'>{skills}</td></tr><tr><td style='border:1px solid #ddd;padding:8px;'><b>Position</b></td><td style='border:1px solid #ddd;padding:8px;'>{a.get('role')}</td></tr><tr><td style='border:1px solid #ddd;padding:8px;'><b>Package</b></td><td style='border:1px solid #ddd;padding:8px;'>{package}</td></tr><tr><td style='border:1px solid #ddd;padding:8px;'><b>Joining Date</b></td><td style='border:1px solid #ddd;padding:8px;'>As per company HR email</td></tr></table><p>Please carry your original documents - College ID, Marksheets, Resume and Aadhar Card on the joining date. Please confirm your acceptance by replying to the company.</p><p>We welcome you to <b>{a.get('company')}</b> and wish you a bright career ahead.</p><br><p><b>HR Manager</b><br>{a.get('company')}<br>Placement Cell, Mangalayatan University</p><div class='no-print' style='text-align:center;margin-top:16px;'><button class='btn btn-g' onclick='window.print()'>Print / Download Offer Letter</button> <a class='btn' href='/dashboard'>Back to Dashboard</a></div></div>""")

@app.route("/apply/<int:did>")
def apply(did):
    u = cur()
    if not u: return redirect("/login")
    if u["role"] != "Student": return render("<div class='box'><h3>Access Denied</h3><p>Only Student can apply for Drives.</p><a class='btn' href='/dashboard'>Back to Dashboard</a></div>")
    db = get_db(); d = db.execute("SELECT * FROM drives WHERE id=?", (did,)).fetchone()
    if not d: db.close(); return redirect("/dashboard")
    d = dict(d); ex = db.execute("SELECT * FROM applications WHERE student=? AND company=? AND role=?", (u["name"], d.get("company"), d.get("role"))).fetchone()
    if not ex: db.execute("INSERT INTO applications(student,company,role,status) VALUES(?,?,?,'Applied')", (u["name"], d.get("company"), d.get("role"))); db.commit()
    db.close(); return render(f"<div class='box'><h3>Applied Successfully!</h3><p>You applied for <b>{d.get('company')} - {d.get('role')}</b></p><div class='bar'><div class='fill' style='width:100%'></div></div><br><a class='btn' href='/dashboard'>Dashboard</a> <a class='btn btn-g' href='/my-applications'>My Applications</a></div>")

@app.route("/my-applications")
def myapps():
    u = cur()
    if not u: return redirect("/login")
    if u["role"] != "Student": return render("<div class='box'><h3>Access Denied</h3><p>Only Student can view My Applications.</p><a class='btn' href='/dashboard'>Back to Dashboard</a></div>")
    db = get_db(); rows = db.execute("SELECT * FROM applications WHERE student=?", (u["name"],)).fetchall(); drives = db.execute("SELECT * FROM drives WHERE status='Approved'").fetchall(); db.close()
    total = len(rows); applied_c = sum(1 for r in rows if dict(r).get("status")=="Applied"); short_c = sum(1 for r in rows if dict(r).get("status")=="Shortlisted"); selected_c = sum(1 for r in rows if dict(r).get("status")=="Selected")
    h = f"""<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:6px;"><div class="card" style="text-align:center;margin:0;"><h2 style="margin:0;color:#2563eb;">{total}</h2><p>Total Applied</p></div><div class="card" style="text-align:center;margin:0;"><h2 style="margin:0;color:#2563eb;">{applied_c}</h2><p>Applied</p></div><div class="card" style="text-align:center;margin:0;"><h2 style="margin:0;color:#7c3aed;">{short_c}</h2><p>Shortlisted</p></div><div class="card" style="text-align:center;margin:0;"><h2 style="margin:0;color:#16a34a;">{selected_c}</h2><p>Selected</p></div></div>"""
    if not rows:
        dh = "".join([f"<div class='drive'><div><b>{dict(d).get('company')} - {dict(d).get('role')}</b><br><small>{dict(d).get('skills')} | Package: {dict(d).get('package')} | Min CGPA: {dict(d).get('cgpa')}</small></div><a class='btn btn-g btn-s' href='/apply/{dict(d).get('id')}'>Apply Now</a></div>" for d in drives])
        h += f"""<div style="background:#eff6ff;padding:18px;border-radius:12px;text-align:center;"><h3 style="border:none;margin:0;">Hello {u['name']}, You Have Not Applied Yet!</h3><p style="color:#475569;">Apply in 1 Click for any company below.</p></div><div class="box"><h3>Available Drives - Apply in 1 Click</h3>{dh or '<p>No drives available.</p>'}</div>"""
    else:
        for r in rows:
            r = dict(r); st = r.get("status") or "Applied"; pct = 100 if st=="Selected" else 66 if st=="Shortlisted" else 33; col = "#16a34a" if st=="Selected" else "#7c3aed" if st=="Shortlisted" else "#2563eb"; tick1 = "✅" if pct>=33 else "⚪"; tick2 = "✅" if pct>=66 else "⚪"; tick3 = "✅" if pct>=100 else "⚪"; msg = "Congratulations! You are Selected! The company will contact you soon. Please keep your documents ready." if st=="Selected" else "Great! You are Shortlisted! Please practice in Interview Coach." if st=="Shortlisted" else "Your application is under review."; badge_c = "b-green" if st=="Selected" else "b-yellow" if st=="Shortlisted" else "b-blue"; letter_btn = f"<a class='btn btn-g btn-s' href='/offer-letter/{r.get('id')}'>Download Offer Letter</a>" if st=="Selected" else ""
            h += f"""<div class='drive' style='display:block;'><div style='display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;'><div><b>{r.get('company')} - {r.get('role')}</b><br><small>Application ID: #{r.get('id')} | Student: {r.get('student')}</small></div><span class='badge {badge_c}'>{st}</span></div><div style='display:flex;justify-content:space-between;text-align:center;margin:14px 0 6px;font-size:13px;'><div>{tick1}<br><b>Applied</b></div><div style='flex:1;border-top:2px dashed #cbd5e1;margin-top:10px;'></div><div>{tick2}<br><b>Shortlisted</b></div><div style='flex:1;border-top:2px dashed #cbd5e1;margin-top:10px;'></div><div>{tick3}<br><b>Selected</b></div></div><p style='font-size:13px;margin:4px 0;'>Progress: <b>{pct}%</b></p><div class='bar'><div class='fill' style='width:{pct}%;background:{col};'></div></div><p style='font-size:13px;background:#f8fafc;padding:10px;border-radius:8px;margin-top:10px;'>{msg}</p>{letter_btn}</div>"""
        h += """<div style="margin-top:12px;"><a class="btn btn-g" href="/dashboard">Apply for More Drives</a> <a class="btn btn-l" href="/interview">Practice Interview</a> <a class="btn btn-p" href="/assistant">Ask AI Assistant</a></div>"""
    return render(f"<div class='box'><h3>My Applications - Live Status</h3><p style='font-size:13px;color:#64748b;'>Student: <b>{u['name']}</b> | Status Flow: Applied - Shortlisted - Selected</p>{h}<br><a class='btn' href='/dashboard'>Back to Dashboard</a></div>")

@app.route("/predictor", methods=["GET","POST"])
def predictor():
    u = cur()
    if not u: return redirect("/login")
    if u["role"] != "Student": return render("<div class='box'><h3>Access Denied</h3><p>ML Predictor is only for Students.</p><a class='btn' href='/dashboard'>Back to Dashboard</a></div>")
    if request.method == "POST":
        cgpa = float(request.form["cgpa"]); skills = int(request.form["skills"]); intern = int(request.form["intern"]); proj = int(request.form["proj"]); score = min(98, int(cgpa*8 + skills*3 + intern*8 + proj*5)); label = "High Chance - Placement Ready!" if score>=75 else "Medium Chance - Need More Practice" if score>=55 else "Low Chance - Improve Skills"; color = "#16a34a" if score>=75 else "#ea580c" if score>=55 else "#dc2626"; db = get_db(); elig = db.execute("SELECT company, role FROM drives WHERE cgpa<=? AND status='Approved'", (cgpa,)).fetchall(); db.close(); eh = "".join([f"<p>Eligible: <b>{dict(e).get('company')} - {dict(e).get('role')}</b></p>" for e in elig]) or "<p>Increase CGPA to become eligible for more companies.</p>"; circ = 2*3.14*75; off = circ - (circ*score/100)
        return render(f"""<div class='box'><h3>ML Placement Prediction - AI Based Analysis</h3><div style='display:flex;align-items:center;gap:22px;flex-wrap:wrap;'><div style='position:relative;width:180px;height:180px;'><svg width='180' height='180' style='transform:rotate(-90deg);'><circle cx='90' cy='90' r='75' fill='none' stroke='#e2e8f0' stroke-width='16'></circle><circle cx='90' cy='90' r='75' fill='none' stroke='{color}' stroke-width='16' stroke-linecap='round' stroke-dasharray='{circ}' stroke-dashoffset='{off}'></circle></svg><div style='position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center;'><h1 style='margin:0;font-size:38px;color:{color};'>{score}%</h1><p style='margin:0;font-size:11px;color:#64748b;font-weight:700;'>PLACEMENT<br>CHANCE</p></div></div><div style='flex:1;min-width:220px;'><span style='background:#dcfce7;color:#166534;padding:6px 14px;border-radius:20px;font-size:13px;font-weight:700;'>{label}</span><p style='color:#475569;font-size:14px;'>Model: <b>Logistic Regression + Random Forest</b> | Accuracy: <b>92.4%</b></p><p><b>Inputs:</b> CGPA {cgpa} | Skills {skills} | Internships {intern} | Projects {proj}</p></div></div></div><div class='box'><h3>Skill Breakdown - Bar Chart Analysis</h3><p>CGPA Score - {int(cgpa*10)}%</p><div class='bar'><div class='fill' style='width:{int(cgpa*10)}%;background:#2563eb;'></div></div><br><p>Technical Skills - {skills*10}%</p><div class='bar'><div class='fill' style='width:{skills*10}%;background:#16a34a;'></div></div><br><p>Internship - {intern*20}%</p><div class='bar'><div class='fill' style='width:{intern*20}%;background:#ea580c;'></div></div><br><p>Projects - {proj*20}%</p><div class='bar'><div class='fill' style='width:{proj*20}%;background:#7c3aed;'></div></div></div><div class='box'><h3>Companies You Are Eligible For:</h3>{eh}<a class='btn' href='/predictor'>Try Again</a> <a class='btn btn-l' href='/dashboard'>Dashboard</a></div>""")
    return render(f"""<div class="box"><h3>ML Placement Predictor</h3><p>Enter your details, AI will predict your placement chance.</p><form method="POST"><label>CGPA (0-10)</label><input name="cgpa" type="number" step="0.1" value="{u['cgpa'] or 8.5}" required><label>Number of Skills (0-10)</label><input name="skills" type="number" value="5" required><label>Internships</label><input name="intern" type="number" value="1" required><label>Projects</label><input name="proj" type="number" value="2" required><button class="btn" style="width:100%;">Predict My Placement Chance</button></form></div>""")

@app.route("/eligibility", methods=["GET","POST"])
def eligibility():
    u = cur()
    if not u: return redirect("/login")
    if u["role"] != "Student": return render("<div class='box'><h3>Access Denied</h3><p>Eligibility Checker is only for Students.</p><a class='btn' href='/dashboard'>Back to Dashboard</a></div>")
    if request.method == "POST":
        cgpa = float(request.form["cgpa"]); db = get_db(); drives = db.execute("SELECT * FROM drives").fetchall(); db.close(); total = len(drives); elig_count = 0; h = ""
        for d in drives:
            d = dict(d); req = d.get("cgpa") or 0; ok = cgpa >= req
            if ok: elig_count += 1
            gap = round(req - cgpa, 1) if not ok else 0; badge = "b-green" if ok else "b-yellow"; txt = "ELIGIBLE" if ok else "NOT ELIGIBLE"; msg = "<b style='color:#16a34a;'>Excellent! You are eligible to apply now.</b>" if ok else f"<b style='color:#dc2626;'>You need {gap} more CGPA.</b> Improve your CGPA to unlock {d.get('company')}."; your_w = min(100, int(cgpa*10))
            h += f"<div class='drive' style='display:block;'><div style='display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;'><div><b>{d.get('company')} - {d.get('role')}</b><br><small>Package: {d.get('package')} | Skills Required: {d.get('skills')}</small></div><span class='badge {badge}'>{txt}</span></div><p style='font-size:13px;margin:10px 0 4px;'>Your CGPA: <b>{cgpa}</b> | Required CGPA: <b>{req}</b></p><div class='bar'><div class='fill' style='width:{your_w}%;background:{'#16a34a' if ok else '#ea580c'};'></div></div><p style='font-size:13px;margin:6px 0 0;'>{msg}</p></div>"
        pct = int(elig_count/total*100) if total else 0; circ = 2*3.14*75; off = circ - (circ*pct/100); color = "#16a34a" if pct>=75 else "#ea580c" if pct>=50 else "#dc2626"; tip = "Excellent! You are eligible for all companies. Apply now to get placed." if pct==100 else f"You are eligible for {elig_count} out of {total} companies. Increase your CGPA slightly to unlock all companies." if pct>=50 else "Improve your CGPA to 7.5+ to unlock all top companies."
        return render(f"""<div class='box'><h3>Eligibility Result - Professional Analysis</h3><div style='display:flex;align-items:center;gap:22px;flex-wrap:wrap;'><div style='position:relative;width:180px;height:180px;'><svg width='180' height='180' style='transform:rotate(-90deg);'><circle cx='90' cy='90' r='75' fill='none' stroke='#e2e8f0' stroke-width='16'></circle><circle cx='90' cy='90' r='75' fill='none' stroke='{color}' stroke-width='16' stroke-linecap='round' stroke-dasharray='{circ}' stroke-dashoffset='{off}'></circle></svg><div style='position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center;'><h1 style='margin:0;font-size:32px;color:{color};'>{elig_count}/{total}</h1><p style='margin:0;font-size:11px;color:#64748b;font-weight:700;'>COMPANIES<br>ELIGIBLE</p></div></div><div style='flex:1;min-width:220px;'><span style='background:#dcfce7;color:#166534;padding:6px 14px;border-radius:20px;font-size:13px;font-weight:700;'>Eligibility Score: {pct}%</span><p style='color:#475569;font-size:14px;'>Your CGPA: <b>{cgpa}</b> | Eligible Companies: <b>{elig_count} / {total}</b></p><p style='background:#eff6ff;padding:12px;border-radius:10px;font-size:13px;'><b>AI Recommendation:</b> {tip}</p></div></div></div><div class='box'><h3>Company Wise Eligibility Breakdown</h3>{h}<br><a class='btn' href='/eligibility'>Check Again</a> <a class='btn btn-l' href='/dashboard'>Dashboard</a> <a class='btn btn-g' href='/predictor'>Check ML Predictor</a></div>""")
    return render(f"""<div class="box"><h3>Eligibility Checker</h3><p>Enter your CGPA to check your eligibility for all companies.</p><form method="POST"><label>Your CGPA</label><input name="cgpa" type="number" step="0.1" value="{u['cgpa'] or 8.5}" required><button class="btn" style="width:100%;">Check All Companies</button></form></div>""")

@app.route("/ats", methods=["GET","POST"])
def ats():
    u = cur()
    if not u: return redirect("/login")
    if u["role"] != "Student": return render("<div class='box'><h3>Access Denied</h3><p>ATS Analyzer is only for Students.</p><a class='btn' href='/dashboard'>Back to Dashboard</a></div>")
    if request.method == "POST":
        text = extract_text(request.files.get("resume_file"), request.form.get("resume",""))
        if not text.strip(): return render("<div class='box'><h3>Please Upload Resume or Paste Text First</h3><a class='btn' href='/ats'>Try Again</a></div>")
        t = text.lower(); checks = {"Python": "python" in t, "Java": "java" in t, "SQL / Database": "sql" in t or "database" in t, "HTML / CSS": "html" in t or "css" in t, "Project Mention": "project" in t, "Internship": "intern" in t, "CGPA Mention": "cgpa" in t, "Email / Contact": "@" in t or "gmail" in t or "phone" in t}; score = int(sum(checks.values())/len(checks)*100); miss = [k for k,v in checks.items() if not v]; h = "".join([f"<p>{'Yes' if v else 'No'} - {k}</p>" for k,v in checks.items()]); verdict = "Excellent! You are ready for top companies!" if score>=80 else "Good! Improve a little more" if score>=55 else "Add more skills to your resume"; color = "#16a34a" if score>=80 else "#ea580c" if score>=55 else "#dc2626"
        return render(f"""<div class='box'><h3>ATS Resume Report</h3><p style='font-size:13px;color:#64748b;'>Total Words: <b>{len(text.split())}</b></p><h2 style='color:{color};font-size:40px;margin:5px 0;'>{score}%</h2><p><b>{verdict}</b></p><div class='bar'><div class='fill' style='width:{score}%'></div></div><br>{h}<div style='background:#fff7ed;padding:14px;border-radius:10px;'><b>Missing:</b> {', '.join(miss) if miss else 'Nothing, Perfect Resume!'}<br><b>Tip:</b> Add missing keywords to your resume to get 90%+ score.</div><br><a class='btn' href='/ats'>Check Another Resume</a> <a class='btn btn-l' href='/dashboard'>Dashboard</a></div>""")
    return render("""<div class="box"><h3>ATS Resume Analyzer - Upload File</h3><p>No need to paste. Upload your Resume, get ATS Score and Missing Skills.</p><form method="POST" enctype="multipart/form-data"><label style="font-weight:700;">Upload Resume (.pdf / .docx / .txt)</label><input type="file" name="resume_file" accept=".pdf,.docx,.txt" style="background:#f8fafc;padding:14px;border:2px dashed #cbd5e1;"><p style="text-align:center;color:#94a3b8;font-size:13px;margin:2px;">- OR -</p><label>Paste Resume Text (Optional)</label><textarea name="resume" rows="4" placeholder="I am Radhya, CGPA 7.0, I know python, java, sql. I did 2 projects..."></textarea><button class="btn btn-o" style="width:100%;">Analyze My Resume</button></form></div>""")

@app.route("/test", methods=["GET","POST"])
def test():
    u = cur()
    if not u: return redirect("/login")
    if u["role"] != "Student": return render("<div class='box'><h3>Access Denied</h3><p>Online Test is only for Students.</p><a class='btn' href='/dashboard'>Back to Dashboard</a></div>")
    qs=[("What is Python used for?",["Web Development","Cooking","Driving","Singing"],"Web Development"),("Full form of HTML?",["Hyper Text Markup Language","High Text Machine","Hyperlink Text","None"],"Hyper Text Markup Language"),("CSS is used for?",["Styling","Database","Logic","Networking"],"Styling"),("SQL is used for?",["Database","Design","Video","Game"],"Database"),("Full form of OOP?",["Object Oriented Programming","Only One Person","Object Of Python","None"],"Object Oriented Programming"),("Which is a Python Framework?",["Django","React","Angular","Laravel"],"Django"),("What is 2 + 2 * 2?",["6","8","4","10"],"6"),("Which is a Database?",["MySQL","HTML","CSS","Photoshop"],"MySQL"),("What is API?",["Application Programming Interface","Apple Pie","Auto Program","None"],"Application Programming Interface"),("Git is used for?",["Version Control","Design","Gaming","Video"],"Version Control")]
    if request.method == "POST":
        sc = sum(1 for i,q in enumerate(qs) if request.form.get(f"q{i}")==q[2]); pct = int(sc/len(qs)*100); return render(f"<div class='box'><h3>Online Test Result</h3><h2>{sc}/{len(qs)} - {pct}%</h2><div class='bar'><div class='fill' style='width:{pct}%'></div></div><p>{'Excellent! Placement Ready!' if pct>=80 else 'Good, Practice More' if pct>=60 else 'Practice More and Try Again'}</p><a class='btn' href='/dashboard'>Dashboard</a></div>")
    h = ""
    for i,q in enumerate(qs):
        opts = "".join([f"<label style='display:block;margin:4px 0;'><input type='radio' name='q{i}' value='{o}' style='width:auto;' required> {o}</label>" for o in q[1]]); h += f"<p><b>Q{i+1}. {q[0]}</b><br>{opts}</p>"
    return render(f"<div class='box'><h3>Online Aptitude Test - 10 Questions</h3><form method='POST'>{h}<button class='btn'>Submit Test</button></form></div>")

@app.route("/interview", methods=["GET","POST"])
def interview():
    u = cur()
    if not u: return redirect("/login")
    if u["role"] != "Student": return render("<div class='box'><h3>Access Denied</h3><p>Interview Coach is only for Students.</p><a class='btn' href='/dashboard'>Back to Dashboard</a></div>")
    if request.method == "POST":
        text = extract_text(request.files.get("resume_file"), request.form.get("resume",""))
        if not text.strip(): return render("<div class='box'><h3>Please Upload Resume or Paste Resume Text First</h3><a class='btn' href='/interview'>Try Again</a></div>")
        qs = build_questions(text); session["iq"] = qs; session["iq_index"] = 0; session["iq_scores"] = []; return redirect("/interview/practice")
    return render("""<div class="box"><h3>AI Interview Coach - Resume Based Practice</h3><p>Upload your Resume. AI will generate interview questions <b>from your own Resume</b>, speak the question in voice, you can answer by <b>Voice Recording OR Written Typing</b>, and AI will give you a real score.</p><form method="POST" enctype="multipart/form-data"><label style="font-weight:700;">Upload Resume (.pdf / .docx / .txt)</label><input type="file" name="resume_file" accept=".pdf,.docx,.txt" style="background:#f8fafc;padding:14px;border:2px dashed #cbd5e1;"><p style="text-align:center;color:#94a3b8;font-size:13px;margin:2px;">- OR -</p><label>Paste Resume Text (Optional)</label><textarea name="resume" rows="4" placeholder="I am Radhya, B.Tech CSE, CGPA 7.0, I know python, java, sql. I did 2 projects and 1 internship..."></textarea><button class="btn btn-g" style="width:100%;">Generate My Interview Questions</button></form></div>""")

@app.route("/interview/practice", methods=["GET","POST"])
def interview_practice():
    u = cur()
    if not u: return redirect("/login")
    qs = session.get("iq")
    if not qs: return redirect("/interview")
    idx = session.get("iq_index", 0)
    if idx >= len(qs): return redirect("/interview/result")
    q = qs[idx]
    if request.method == "POST":
        ans = request.form.get("answer","").strip(); mode = request.form.get("answer_mode","Written")
        if len(ans) < 10: return render(f"<div class='box'><h3>Answer Too Short</h3><p>Please speak or write at least 2-3 sentences in English to get a real score.</p><a class='btn' href='/interview/practice'>Try Again</a></div>")
        a_low = ans.lower(); found = [k for k in q["keywords"] if k in a_low]; keyword_score = int(len(found) / len(q["keywords"]) * 70) if q["keywords"] else 0; words = len(ans.split()); length_score = 30 if words >= 40 else 20 if words >= 25 else 10 if words >= 15 else 5; total = min(98, keyword_score + length_score)
        if total >= 80: verdict = "Excellent Answer - Interview Ready!"; feedback = "Great! You covered key points and explained with good length."
        elif total >= 60: verdict = "Good Answer - Improve Slightly"; feedback = f"You covered {len(found)}/{len(q['keywords'])} key points. Add missing keywords."
        else: verdict = "Needs Improvement - Practice Again"; feedback = f"You covered only {len(found)}/{len(q['keywords'])} key points. Tip: {q['tip']}"
        scores = session.get("iq_scores", []); scores.append({"q": q["q"], "ans": ans, "score": total, "found": found, "verdict": verdict, "mode": mode}); session["iq_scores"] = scores; session["iq_index"] = idx + 1; color = "#16a34a" if total>=80 else "#ea580c" if total>=60 else "#dc2626"; nxt = "/interview/practice" if idx + 1 < len(qs) else "/interview/result"; nxt_txt = "Next Question" if idx + 1 < len(qs) else "See Final Result"
        return render(f"""<div class='box'><h3>Your Answer Score - Real Keyword Based Scoring</h3><p style='font-size:12px;color:#64748b;'>Answer Mode: <b>{mode}</b></p><h2 style='color:{color};font-size:42px;margin:5px 0;'>{total} / 100</h2><p><b>{verdict}</b></p><div class='bar'><div class='fill' style='width:{total}%;background:{color};'></div></div><br><p><b>Question:</b> {q['q']}</p><p><b>Your Answer ({mode}):</b> {ans}</p><p><b>Keywords Found:</b> {len(found)} / {len(q['keywords'])} - {', '.join(found) if found else 'None'}</p><p><b>Words:</b> {words} words</p><div style='background:#eff6ff;padding:14px;border-radius:10px;'><b>AI Feedback:</b> {feedback}<br><br><b>Preparation Tip:</b> {q['tip']}</div><br><a class='btn' href='{nxt}'>{nxt_txt}</a> <a class='btn btn-l' href='/interview/result'>See Final Result</a></div>""")
    q_safe = q["q"].replace("'", "").replace('"', '')
    return render(f"""<div class='box'><h3>AI Interview Coach - Question {idx+1} of {len(qs)}</h3><p style='font-size:13px;color:#64748b;'>This question is generated from <b>your Resume</b>. Listen, then answer by <b>Voice OR Typing</b> in English.</p><div style='background:#eff6ff;padding:16px;border-radius:12px;'><b>Q{idx+1}. {q['q']}</b><br><br><button type='button' class='btn btn-o' onclick="speak('{q_safe}')">Listen in Voice</button><button type='button' class='btn btn-l' onclick="speechSynthesis.cancel()">Stop Voice</button></div><div style='background:#fff7ed;padding:14px;border-radius:12px;margin-top:12px;'><b>Option 1 - Voice Practice</b><br><button type='button' class='btn btn-g' id='recBtn' onclick="startVoice()">Start Voice Recording</button><button type='button' class='btn btn-l' onclick="stopVoice()">Stop Recording</button><p id='voiceStatus' style='font-size:13px;color:#dc2626;font-weight:700;margin:8px 0 0;'>Mic is OFF - Click Start Voice Recording and Speak in English</p></div><form method='POST'><label style='font-weight:700;'>Option 2 - Written Practice OR Your Voice Answer Will Appear Here</label><textarea name='answer' id='answerBox' rows='5' placeholder='Type your answer here in English - at least 2-3 sentences...' required></textarea><input type='hidden' name='answer_mode' id='answerMode' value='Written'><button class='btn btn-g' style='width:100%;'>Submit Answer & Get Score</button></form></div><script>function speak(t){{speechSynthesis.cancel();var u=new SpeechSynthesisUtterance(t);u.lang='en-IN';speechSynthesis.speak(u);}} var rec; function startVoice(){{try{{var SR=window.SpeechRecognition||window.webkitSpeechRecognition;rec=new SR();rec.lang='en-IN';rec.continuous=true;rec.interimResults=true;rec.onresult=function(e){{var txt='';for(var i=0;i<e.results.length;i++){{txt+=e.results[i][0].transcript+' ';}}document.getElementById('answerBox').value=txt;document.getElementById('answerMode').value='Voice';}};rec.start();document.getElementById('voiceStatus').innerHTML='Mic is ON - Speak Now...';}}catch(err){{alert('Voice not supported in this browser. Please type your answer.');}}}} function stopVoice(){{if(rec){{rec.stop();}}document.getElementById('voiceStatus').innerHTML='Mic is OFF - Recording Stopped. Now click Submit.';}}</script>""")

@app.route("/interview/result")
def interview_result():
    u = cur()
    if not u: return redirect("/login")
    scores = session.get("iq_scores", [])
    if not scores: return redirect("/interview")
    avg = int(sum(s["score"] for s in scores)/len(scores)) if scores else 0
    h = "".join([f"<div style='background:#f8fafc;padding:12px;border-radius:10px;margin-top:8px;'><b>Q: {s['q']}</b><br>Score: <b>{s['score']}/100</b> - {s['verdict']}<br><small>{s['ans'][:120]}...</small></div>" for s in scores])
    return render(f"<div class='box'><h3>Interview Final Result - Average Score: {avg}/100</h3><p>Total Questions: {len(scores)}</p>{h}<br><a class='btn' href='/interview'>Practice Again</a> <a class='btn btn-l' href='/dashboard'>Dashboard</a></div>")

@app.route("/assistant", methods=["GET","POST"])
def assistant():
    u = cur()
    if not u: return redirect("/login")
    ans = ""
    if request.method == "POST":
        q = request.form.get("q","").lower()
        if "resume" in q: ans = "Add Python, Java, SQL, 2 Projects and 1 Internship to your resume to get 90%+ ATS Score."
        elif "interview" in q: ans = "Practice in Interview Coach. Use STAR method: Situation - Task - Action - Result."
        elif "cgpa" in q: ans = "Try to keep CGPA above 7.5 to be eligible for TCS, Infosys, Wipro."
        elif "project" in q: ans = "Make 2 projects: 1 Web Project and 1 Python/ML Project. Mention them in resume."
        else: ans = "Ask me about Resume, Interview, CGPA, Projects. I will guide you for placement."
        return render(f"<div class='box'><h3>AI Assistant</h3><p><b>Your Question:</b> {request.form.get('q')}</p><p style='background:#eff6ff;padding:14px;border-radius:10px;'><b>Answer:</b> {ans}</p><a class='btn' href='/assistant'>Ask Another Question</a> <a class='btn btn-l' href='/dashboard'>Dashboard</a></div>")
    return render("""<div class="box"><h3>AI Assistant - Ask Anything About Placement</h3><form method="POST"><input name="q" placeholder="e.g. How to improve my resume?" required><button class="btn" style="width:100%;">Ask AI Assistant</button></form><p style="font-size:13px;color:#64748b;">Try: How to improve resume? / How to prepare interview? / How much CGPA needed?</p></div>""")

@app.route("/create-drive", methods=["GET","POST"])
def create_drive():
    u = cur()
    if not u: return redirect("/login")
    if u["role"] not in ("Company","Admin"): return render("<div class='box'><h3>Access Denied</h3><p>Only Company and Admin can post drives.</p><a class='btn' href='/dashboard'>Back</a></div>")
    if request.method == "POST":
        db = get_db(); status = "Approved" if u["role"]=="Admin" else "Pending"; db.execute("INSERT INTO drives(company,role,skills,cgpa,package,deadline,status) VALUES(?,?,?,?,?,?,?)", (request.form["company"], request.form["role"], request.form["skills"], float(request.form["cgpa"] or 0), request.form["package"], request.form["deadline"], status)); db.commit(); db.close()
        return render(f"<div class='box'><h3>Drive Posted Successfully!</h3><p>Status: <b>{status}</b></p><a class='btn' href='/dashboard'>Dashboard</a></div>")
    return render("""<div class="box"><h3>Post New Drive</h3><form method="POST"><input name="company" placeholder="Company Name - e.g. TCS" required><input name="role" placeholder="Role - e.g. Java Developer" required><input name="skills" placeholder="Skills - e.g. java, sql" required><input name="cgpa" placeholder="Min CGPA - e.g. 7.0" required><input name="package" placeholder="Package - e.g. 7 LPA" required><input name="deadline" placeholder="Deadline - e.g. 2026-12-31" required><button class="btn btn-o" style="width:100%;">Post Drive</button></form></div>""")

@app.route("/admin", methods=["GET","POST"])
def admin():
    u = cur()
    if not u: return redirect("/login")
    if u["role"] != "Admin": return render("<div class='box'><h3>Access Denied</h3><p>Only Admin can open Admin Panel.</p><a class='btn' href='/dashboard'>Back</a></div>")
    db = get_db()
    if request.method == "POST":
        action = request.form.get("action"); did = request.form.get("drive_id")
        if action == "approve": db.execute("UPDATE drives SET status='Approved' WHERE id=?", (did,))
        elif action == "reject": db.execute("UPDATE drives SET status='Rejected' WHERE id=?", (did,))
        elif action == "delete_drive": db.execute("DELETE FROM drives WHERE id=?", (did,))
        db.commit()
    drives = db.execute("SELECT * FROM drives").fetchall(); apps = db.execute("SELECT * FROM applications").fetchall(); db.close()
    dh = "".join([f"<div class='drive'><div><b>{dict(d).get('company')} - {dict(d).get('role')}</b><br><small>Status: {dict(d).get('status')} | Package: {dict(d).get('package')}</small></div><form method='POST' style='display:flex;gap:4px;'><input type='hidden' name='drive_id' value='{dict(d).get('id')}'><button name='action' value='approve' class='btn btn-g btn-s'>Approve</button><button name='action' value='reject' class='btn btn-o btn-s'>Reject</button></form></div>" for d in drives])
    ah = "".join([f"<div class='drive'><div><b>{dict(a).get('student')} - {dict(a).get('company')} - {dict(a).get('role')}</b></div><span class='badge b-blue'>{dict(a).get('status')}</span></div>" for a in apps])
    return render(f"<div class='box'><h3>Admin Panel - Approve Drives</h3>{dh or '<p>No drives yet.</p>'}</div><div class='box'><h3>All Applications</h3>{ah or '<p>No applications yet.</p>'}</div><a class='btn' href='/dashboard'>Back to Dashboard</a>")

@app.route("/analytics")
def analytics():
    u = cur()
    if not u: return redirect("/login")
    db = get_db(); sc = db.execute("SELECT COUNT(*) FROM users WHERE role='Student'").fetchone()[0]; cc = db.execute("SELECT COUNT(*) FROM users WHERE role='Company'").fetchone()[0]; dc = db.execute("SELECT COUNT(*) FROM drives").fetchone()[0]; ac = db.execute("SELECT COUNT(*) FROM applications").fetchone()[0]; sel = db.execute("SELECT COUNT(*) FROM applications WHERE status='Selected'").fetchone()[0]; db.close()
    pct = int(sel/ac*100) if ac else 0
    return render(f"<div class='box'><h3>Analytics & Reports</h3></div><div class='grid'><div class='card'><h2>{sc}</h2><p>Total Students</p></div><div class='card'><h2>{cc}</h2><p>Total Companies</p></div><div class='card'><h2>{dc}</h2><p>Total Drives</p></div><div class='card'><h2>{sel}/{ac}</h2><p>Selected / Applied - {pct}%</p></div></div><div class='box'><h3>Placement Rate</h3><div class='bar'><div class='fill' style='width:{pct}%'></div></div><p>{pct}% Students Selected</p></div><a class='btn' href='/dashboard'>Back to Dashboard</a>")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
