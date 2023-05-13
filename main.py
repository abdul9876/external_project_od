from fastapi import FastAPI, Request, Depends, HTTPException, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import sqlite3

app = FastAPI()

security = HTTPBasic()

templates = Jinja2Templates(directory="templates")
#db_filename = 'dashboard.db'




def create_tables():
    conn = sqlite3.connect('dashboard.db')
    cur = conn.cursor()
    # Create the users table if it doesn't exist
    users_table = '''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    );
    '''
    cur.execute(users_table)

    # Create the documents table if it doesn't exist
    documents_table = '''
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY,
        filename TEXT NOT NULL UNIQUE,
        filepath TEXT NOT NULL,
        status TEXT NOT NULL,
        uploaded_by TEXT NOT NULL,
        approved_by TEXT,
        FOREIGN KEY (uploaded_by) REFERENCES users(username),
        FOREIGN KEY (approved_by) REFERENCES users(username)
    );
    '''
    cur.execute(documents_table)

    # Commit the changes to the database and close the connection
    conn.commit()


def get_current_user(username, password, role):
    #user = None
    conn = sqlite3.connect('dashboard.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = ? AND password = ? AND role = ?", (username, password, role))
    row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    #user = dict(row)
    #print(row)
    return row

def display_student_hist(username):
    conn = sqlite3.connect('dashboard.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM documents WHERE uploaded_by = ?", (username,))
    rows = cur.fetchall()
    students = []
    for row in rows:
        student = {"file_name": row[1], "status": row[3]}
        students.append(student)
    conn.close()
    return students

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    create_tables()
    template = "index.html"
    return templates.TemplateResponse(template, {"request": request})

@app.post("/login")
def login(username: str = Form(...), password: str = Form(...), role: str = Form(...)):
    row = get_current_user(username, password, role)
    if row[3] == 'student':
        return RedirectResponse(url="/student/"+row[1])
    elif row[3] == 'fa':
        return RedirectResponse(url="/fa/"+row[1])
    elif row[3] == 'aa':
        return RedirectResponse(url="/aa/"+row[1])
    elif row[3] == 'hod':
        return RedirectResponse(url="/hod/"+row[1])
    #print(username, password, role)

@app.post("/student/{username}")
def student_dashboard(request: Request, username: str):
    students = display_student_hist(username)
    template = "student.html"
    return templates.TemplateResponse(template, {"request": request, "username": username, "students": students})

@app.post("/fa/{username}")
def fa_dashboard(request: Request, username: str):
    template = "fa.html"
    return templates.TemplateResponse(template, {"request": request, "username": username})

@app.post("/aa/{username}")
def student_dashboard(request: Request, username: str):
    template = "aa.html"
    return templates.TemplateResponse(template, {"request": request, "username": username})

@app.post("/hod/{username}")
def fa_dashboard(request: Request, username: str):
    template = "hod.html"
    return templates.TemplateResponse(template, {"request": request, "username": username})



