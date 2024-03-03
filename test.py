from fastapi import FastAPI, Request, Depends, HTTPException, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import JSONResponse
import sqlite3

app = FastAPI()

security = HTTPBasic()

templates = Jinja2Templates(directory="templates")

def create_tables():
    conn = sqlite3.connect('dashboard4.db')
    cur = conn.cursor()
    # Create the users table if it doesn't exist
    users_table = '''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        dep TEXT NOT NULL,
        section TEXT NOT NULL
    );
    '''
    cur.execute(users_table)

    # Create the documents table if it doesn't exist
    documents_table = '''
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY,
        ODcount INT DEFAULT 0,
        MLcount INT DEFAULT 0,
        filetype TEXT NOT NULL CHECK(filetype=='OD' OR filetype=='ML'),
        fa_status TEXT NOT NULL ,
        aa_status TEXT NOT NULL DEFAULT 'processing',
        hod_status TEXT NOT NULL DEFAULT 'processing',
        uploaded_by TEXT NOT NULL,
        dep TEXT NOT NULL,
        section TEXT NOT NULL
    );
    '''
    cur.execute(documents_table)

    # Commit the changes to the database and close the connection
    conn.commit()

def get_current_user(username, password, role):
    #user = None
    conn = sqlite3.connect('dashboard4.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = ? AND password = ? AND role = ?", (username, password, role))
    row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    #user = dict(row)
    #print(row)
    return row

def display_student_hist(username):
    conn = sqlite3.connect('dashboard4.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM documents WHERE uploaded_by = ?", (username,))
    rows = cur.fetchall()
    #print(rows)
    students = []
    for row in rows:
        student = {"file_type": row[3], "ODcount": row[1], "MLcount": row[2], "fa_status":row[4],"aa_status":row[5],"hod_status":row[6]}
        students.append(student)
    conn.close()
    #print(students)
    return students

def display_fa_hist(username):
    conn = sqlite3.connect('dashboard4.db')
    cur = conn.cursor()
    cur.execute("SELECT section FROM users WHERE username = ?", (username,))
    sec = cur.fetchone()
    cur.execute("SELECT * FROM documents WHERE section= ?", (sec[0],))
    rows = cur.fetchall()
    #print(rows)
    docs=[]
    for row in rows:
        doc = {"uploaded_by": row[7], "file_type": row[3], "status": row[4], "ODid": row[1],"MLid":row[2]}
        docs.append(doc)
    conn.close()
    return docs

def display_aa_hist(username):
    conn = sqlite3.connect('dashboard4.db')
    cur = conn.cursor()
    cur.execute("SELECT dep FROM users WHERE username = ?", (username,))
    dep = cur.fetchone()
    cur.execute("SELECT * FROM documents WHERE dep= ? AND fa_status = ?", (dep[0],"approved",))
    rows = cur.fetchall()
    #print(rows)
    docs=[]
    for row in rows:
        doc = {"uploaded_by": row[7], "file_type": row[3], "status": row[5], "ODid": row[1],"MLid":row[2]}
        docs.append(doc)
    conn.close()
    #print(docs)
    return docs

def display_hod_hist(username):
    conn = sqlite3.connect('dashboard4.db')
    cur = conn.cursor()
    cur.execute("SELECT dep FROM users WHERE username = ?", (username,))
    dep = cur.fetchone()
    cur.execute("SELECT * FROM documents WHERE dep= ? AND aa_status = ?", (dep[0],"approved",))
    rows = cur.fetchall()
    #print(rows)
    docs=[]
    for row in rows:
        doc = {"uploaded_by": row[7], "file_type": row[3], "status": row[6], "ODid": row[1],"MLid":row[2]}
        docs.append(doc)
    conn.close()
    #print(docs)
    return docs

def update_status(username):
    conn = sqlite3.connect('dashboard4.db')
    cur = conn.cursor()
    cur.execute("SELECT section FROM users WHERE username = ?", (username,))
    sec = cur.fetchone()
    cur.execute("SELECT uploaded_by FROM documents WHERE section= ?", (sec[0],))
    rows = cur.fetchall()
    stud_list=[]
    for row in rows:
        stu={"stu":row[0]}
        stud_list.append(stu)
    conn.close()
    return stud_list

def update_status_aa(username):
    conn = sqlite3.connect('dashboard4.db')
    cur = conn.cursor()
    cur.execute("SELECT dep FROM users WHERE username = ?", (username,))
    dep = cur.fetchone()
    
    cur.execute("SELECT uploaded_by FROM documents WHERE dep= ? AND fa_status = ?", (dep[0],"approved",))
    rows = cur.fetchall()
    #print(rows)
    stud_list=[]
    for row in rows:
        stu={"stu":row[0]}
        stud_list.append(stu)
    conn.close()
    #print(stud_list)
    return stud_list

def update_status_hod(username):
    conn = sqlite3.connect('dashboard4.db')
    cur = conn.cursor()
    cur.execute("SELECT dep FROM users WHERE username = ?", (username,))
    dep = cur.fetchone()
    
    cur.execute("SELECT uploaded_by FROM documents WHERE dep= ? AND aa_status = ?", (dep[0],"approved",))
    rows = cur.fetchall()
    #print(rows)
    stud_list=[]
    for row in rows:
        stu={"stu":row[0]}
        stud_list.append(stu)
    conn.close()
    #print(stud_list)
    return stud_list

def approveOD(studentid,doctype,number):
    conn = sqlite3.connect('dashboard4.db')
    cur = conn.cursor()
    cur.execute("UPDATE documents SET fa_status= ? WHERE uploaded_by = ? AND filetype = ? AND ODcount = ?", ('approved',studentid,doctype,number,))
    conn.commit()
    conn.close()

def approveML(studentid,doctype,number):
    conn = sqlite3.connect('dashboard4.db')
    cur = conn.cursor()
    cur.execute("UPDATE documents SET fa_status= ? WHERE uploaded_by = ? AND filetype = ? AND MLcount = ?", ('approved',studentid,doctype,number,))
    conn.commit()
    conn.close()

def approveODAA(studentid,doctype,number):
    conn = sqlite3.connect('dashboard4.db')
    cur = conn.cursor()
    cur.execute("UPDATE documents SET aa_status= ? WHERE uploaded_by = ? AND filetype = ? AND ODcount = ?", ('approved',studentid,doctype,number,))
    conn.commit()
    conn.close()

def approveMLAA(studentid,doctype,number):
    conn = sqlite3.connect('dashboard4.db')
    cur = conn.cursor()
    cur.execute("UPDATE documents SET aa_status= ? WHERE uploaded_by = ? AND filetype = ? AND MLcount = ?", ('approved',studentid,doctype,number,))
    conn.commit()
    conn.close()

def approveODHOD(studentid,doctype,number):
    conn = sqlite3.connect('dashboard4.db')
    cur = conn.cursor()
    cur.execute("UPDATE documents SET hod_status= ? WHERE uploaded_by = ? AND filetype = ? AND ODcount = ?", ('approved',studentid,doctype,number,))
    conn.commit()
    conn.close()

def approveMLHOD(studentid,doctype,number):
    conn = sqlite3.connect('dashboard4.db')
    cur = conn.cursor()
    cur.execute("UPDATE documents SET hod_status= ? WHERE uploaded_by = ? AND filetype = ? AND MLcount = ?", ('approved',studentid,doctype,number,))
    conn.commit()
    conn.close()

def get_ODcount(s_id):
    conn = sqlite3.connect('dashboard4.db')
    cur = conn.cursor()
    cur.execute("SELECT ODcount from documents WHERE uploaded_by = ?", (s_id,))
    ODs = cur.fetchall()
    if len(ODs)==0:
        conn.close()
        return 0
    else:
        MAX = max(ODs)[0]
        conn.close()
        return MAX

def uploadOD(doctype,s_id,dep,sec):
    conn = sqlite3.connect('dashboard4.db')
    MAX = get_ODcount(s_id)
    cur=conn.cursor()
    cur.execute("INSERT INTO documents (ODcount,filetype,fa_status,uploaded_by,dep,section) VALUES (?,?,?,?,?,?) ",(MAX+1,doctype,"processing",s_id,dep,sec) )
    #get_ODcount()
    conn.commit()
    conn.close()

def get_MLcount(s_id):
    conn = sqlite3.connect('dashboard4.db')
    cur = conn.cursor()
    cur.execute("SELECT MLcount from documents WHERE uploaded_by = ?", (s_id,))
    ODs = cur.fetchall()
    if len(ODs)==0:
        conn.close()
        return 0
    else:
        MAX = max(ODs)[0]
        conn.close()
        return MAX

def uploadML(doctype,s_id,dep,sec):
    conn = sqlite3.connect('dashboard4.db')
    MAX = get_MLcount(s_id)
    cur=conn.cursor()
    cur.execute("INSERT INTO documents (MLcount,filetype,fa_status,uploaded_by,dep,section) VALUES (?,?,?,?,?,?) ",(MAX+1,doctype,"processing",s_id,dep,sec) )
    #get_ODcount()
    conn.commit()
    conn.close()

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    create_tables()
    template = "homepage.html"
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

@app.post("/student/{username}/applyOD")
#doctype,s_id,dep,sec
def applyOD(request: Request, username: str,doctype: str = Form(...),s_id: str = Form(...), dep: str = Form(...),sec: str = Form(...)):
    students = display_student_hist(username)
    print(doctype,s_id,dep,sec)
    if doctype == "OD":
        uploadOD(doctype,s_id,dep,sec)
    elif doctype == "ML":   
        uploadML(doctype,s_id,dep,sec)
    #get_ODcount()
    #return JSONResponse({"doctype": doctype,
    #                     "s_id" : s_id,
    #                     "dep" : dep,
    #                     "sec" : sec
    #                     })
    template = "student.html"
    return templates.TemplateResponse(template, {"request": request, "username": username, "students": students})

@app.post("/fa/{username}")
def fa_dashboard(request: Request, username: str):
    docs = display_fa_hist(username)
    stud_list=update_status(username)
    template = "fa.html"
    return templates.TemplateResponse(template, {"request": request, "username": username, "docs": docs,"stud_list":stud_list})

@app.post("/fa/{username}/action")
def action(request: Request,username: str,studentid: str = Form(...), doctype: str = Form(...), ODid:str = Form(...), MLid:str = Form(...)):
    if doctype=='OD':
        approveOD(studentid, doctype,ODid)
    elif doctype=='ML':
        approveML(studentid, doctype,MLid)
    docs = display_fa_hist(username)
    stud_list=update_status(username)
    template = "fa.html"
    return templates.TemplateResponse(template, {"request": request, "username": username, "docs": docs,"stud_list":stud_list})
    
@app.post("/aa/{username}")
def student_dashboard(request: Request, username: str):
    docs = display_aa_hist(username)
    stud_list=update_status_aa(username)
    template = "aa.html"
    return templates.TemplateResponse(template, {"request": request, "username": username, "docs": docs,"stud_list":stud_list})

@app.post("/aa/{username}/action")
def action(request: Request,username: str,studentid: str = Form(...), doctype: str = Form(...), ODid:str = Form(...), MLid:str = Form(...)):
    if doctype=='OD':
        approveODAA(studentid, doctype,ODid)
    elif doctype=='ML':
        approveMLAA(studentid, doctype,MLid)
    docs = display_aa_hist(username)
    stud_list=update_status_aa(username)
    template = "aa.html"
    return templates.TemplateResponse(template, {"request": request, "username": username, "docs": docs,"stud_list":stud_list})

@app.post("/hod/{username}")
def fa_dashboard(request: Request, username: str):
    docs = display_hod_hist(username)
    stud_list=update_status_hod(username)
    template = "hod.html"
    return templates.TemplateResponse(template, {"request": request, "username": username, "docs":docs, "stud_list": stud_list})

@app.post("/hod/{username}/action")
def action(request: Request,username: str,studentid: str = Form(...), doctype: str = Form(...), ODid:str = Form(...), MLid:str = Form(...)):
    if doctype=='OD':
        approveODHOD(studentid, doctype,ODid)
    elif doctype=='ML':
        approveMLHOD(studentid, doctype,MLid)
    docs = display_hod_hist(username)
    stud_list=update_status_hod(username)
    template = "hod.html"
    return templates.TemplateResponse(template, {"request": request, "username": username, "docs": docs,"stud_list":stud_list})