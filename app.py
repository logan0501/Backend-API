from __future__ import print_function
from flask import Flask,jsonify,request
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os
from dotenv import load_dotenv
import requests
import json
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
import tempfile
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import random

load_dotenv()
API_KEY = os.getenv('KEY')

cred = credentials.Certificate("secret_key.json")
firebase_admin.initialize_app(cred)
firestoreDb = firestore.client()

SCOPES = ['https://www.googleapis.com/auth/drive']


from flask_cors import CORS, cross_origin
app = Flask(__name__)
cors = CORS(app)


def get_gdrive_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        return build('drive', 'v3', credentials=creds)
    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')
service = get_gdrive_service()

def createFolder(service,uid):
    try: 
        file_metadata = {
            'name': uid,
            'mimeType': 'application/vnd.google-apps.folder',
            "parents":["149uIJHmu2USVA0FaYkCEyTz2l3Le7AfM"]
        }

        file = service.files().create(body=file_metadata, fields='id'
                                      ).execute()
        # print(F'Folder ID: "{file.get("id")}".')
        print("[] Folder created")
        return file.get('id')

    except HttpError as error:
        return jsonify({"error":error }),400

def SignUp(email,password,userData,userType):
    signUpUrl = "https://identitytoolkit.googleapis.com/v1/accounts:signUp?key="+API_KEY
    data =json.dumps({"email":email,"password":password,"returnSecureToken":True})
    res = requests.post(signUpUrl,data=data)
    res=res.json()
    if("localId" in res):
        print("[] "+userType+" created student user account")
        uid = res['localId']
        userData['uid'] = uid
        folderId = createFolder(service,uid)
        if folderId:
            userData['folderId']=folderId
            dbRes = firestoreDb.collection(userType+'s').document(uid).set(userData)
            if (dbRes):
                return jsonify({"data":{userType:res},"message":"Successfully created new user"}),200
            else:
                return jsonify({"error":"Error occured while creating folder in gdriver" }),400
        else:
            return jsonify({"error":"Error occured while uploading data to firestore" }),400
    if("error" in res):
        print("[] Error occurred")
        return jsonify({"error":res["error"]["message"] }),400

def LogIn(email,passoword,userType):
    loginUrl = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key="+API_KEY
    data =json.dumps({"email":email,"password":passoword,"returnSecureToken":True})
    res = requests.post(loginUrl,data=data)
    res = res.json()
    if("localId" in res):
        doc_ref = firestoreDb.collection(userType+'s').document(res['localId'])
        doc = doc_ref.get()
        if doc.exists:
            print("[] "+userType+" data found")
            return jsonify({"data":{userType:res},"message":userType+" data found"}),200
        else:
            print("[] user trying to cheat");
            return jsonify({"error":"Access denied for the user"}),400
    if("error" in res):
        print("[] Error occured")
        return jsonify({"error":res["error"]["message"] }),400

# ---- Signup users ----
@app.route("/signup-student",methods =['POST','GET'])
def signUpStudent():
    if (request.method == 'POST'):
        studentData = request.get_json()
        studentEmail = studentData['studentEmail']
        studentPassword = studentData['studentPassword']
        print("[] Student data received for signup")
        return SignUp(studentEmail,studentPassword,studentData,'student')
        
@app.route("/signup-teacher",methods=['POST','GET'])    
def signUpTeacher():
    if (request.method =='POST'):
        teacherData = request.get_json()
        teacherEmail = teacherData['teacherEmail']
        teacherPassword = teacherData['teacherPassword']
        print("[] Teacher data received for signup")
        return SignUp(teacherEmail,teacherPassword,teacherData,'teacher')

@app.route("/login-student",methods=["POST","GET"])
def LoginStudent():
    if (request.method == 'POST'):
        studentData = request.get_json()
        studentEmail = studentData['studentEmail']
        studentPassword = studentData['studentPassword']
        return LogIn(studentEmail,studentPassword,'student')

@app.route("/login-teacher",methods=["POST","GET"])
def LoginTeacher():
    if (request.method == 'POST'):
        teacherData = request.get_json()
        teacherEmail = teacherData['teacherEmail']
        teacherPassword = teacherData['teacherPassword']
        return LogIn(teacherEmail,teacherPassword,'teacher')
def uploadFile(service,temp,filename,folderId):
 
    # 149uIJHmu2USVA0FaYkCEyTz2l3Le7AfM
    try:

        file_metadata = {'name': filename,"parents":[folderId]}
        media = MediaFileUpload(temp.name,
                                mimetype='application/pdf')
        # pylint: disable=maybe-no-member
        file = service.files().create(body=file_metadata, media_body=media,
                                      fields='webViewLink,id',supportsAllDrives=True).execute()

        print(F'[] File uploaded')
        return [file.get('id'),file.get('webViewLink')]
    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None
    os.remove(temp.name)
    return [file.get('id'),file.get('webViewLink')]

def sendNoteVerificationEmail(user,file,uId,fileId,subject):
    print("[] Email service initiated")
    temp = tempfile.NamedTemporaryFile(delete=False)
    file.save(temp.name)
    EMAIL = os.getenv('EMAIL')
    PASSWORD = os.getenv('PASSWORD')
    fromaddr = EMAIL
    toaddr = user['studentEmail']
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Verification of notes"
    msg['From'] = fromaddr
    msg['To'] = toaddr
    html ="""<!DOCTYPE html>
    <html lang="en">
    <head></head>
    <body>
        <h1>Notely : Notification for verifying the notes</h1>
        <p>
        """+user['studentName']+""" has published a note on """+subject+""", we would like to know
        whether the content in the note shared by them is appropriate and relavant.
        After reviewing the attachment kindly accept or reject the notes.
        </p>
        <p>
          <a href="https://notely-cit.web.app/note-accept?voterid="""+user['uid']+"""&userid="""+uId+"""&noteid="""+fileId+"""\">Click Here</a>
          <span> to accept the note.</span>
        </p>
        <p>
          <a href="https://notely-cit.web.app/note-reject?voterid="""+user['uid']+"""&userid="""+uId+"""&noteid="""+fileId+"""\">Click Here</a>
          <span> to reject the note.</span>
        </p>
        <br/>
        <h4>Thank you</h4>
        <p>Regards,</p>
        <p>Team Notely.</p>
    </body>
    </html>

        """
    msg.attach(MIMEText(html, 'html'))
    attachment = open(temp.name, "rb")
    p = MIMEBase('application', 'octet-stream')
    p.set_payload((attachment).read())
    encoders.encode_base64(p)
    p.add_header('Content-Disposition', "attachment; filename= %s" % file.filename)
    msg.attach(p)
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(EMAIL,"udvgimfcrssasnlf")
    message = msg.as_string()
    s.sendmail(EMAIL, toaddr, message)
    s.quit()
    os.remove(temp.name)
    print("[] Email sent for verification")
@app.route("/upload-note",methods=["POST","GET"])
def uploadNotes():
    if (request.method=='POST'):
        file = request.files['file']
 
        uploaddata = json.loads(request.form['data'])
        uId = uploaddata['uId']
        userType = uploaddata["userType"]
        subject= uploaddata['subjectName']
        temp = tempfile.NamedTemporaryFile(delete=False)
        file.save(temp.name)
        doc_ref  = firestoreDb.collection(userType+'s').document(uId)

        if doc_ref:
            doc = doc_ref.get().to_dict()
            folderId = doc["folderId"]
            [fileId,fileLink] = uploadFile(service,temp,file.filename,folderId)
            if fileId:
                uploaddata["isAdminApproved"]=False
                uploaddata["fileId"]=fileId
                uploaddata["fileLink"]=fileLink
                firestoreDb.collection(uId).document(fileId).set({"fileId":fileId,"uId":uId})
                dbRes = firestoreDb.collection("notes").document(fileId).set(uploaddata)
                if dbRes:
                    docs = firestoreDb.collection(u'students').stream()
                    userDict =dict()
                    for doc in docs:
                        userDict[doc.id] = doc.to_dict()
                    randomUsers=[]
                    while len(randomUsers)<2:
                        choice = random.choice( list(userDict.keys()))
                        if choice not in randomUsers and choice!=uId:
                            randomUsers.append(choice)
                    # print(randomUsers)
                    for user in randomUsers:
                        sendNoteVerificationEmail(userDict[user],file,uId,fileId,subject)
                    return jsonify({"message":"File uploaded sucessfully and currently in verification phase","filedId":fileId }),200
                else:
                    return jsonify({"error":"Error while uploading the file"}),500
            else:
                print("[] Error while uploading the file")
                return jsonify({"error":"Error while uploading the file"}),500
        else:
            print("[] Error while retreiving the document from firebase.")
            return jsonify({"error":"Error while retreving the document from firebase"}),500
    

def sendNoteVerifiedEmail(recEmail,html):
    print("[]Verified Email Initiated")
    EMAIL = os.getenv('EMAIL')
    PASSWORD = os.getenv('PASSWORD')
    fromaddr = EMAIL
    toaddr = recEmail

    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Verification of notes"
    msg['From'] = fromaddr
    msg['To'] = toaddr

    msg.attach(MIMEText(html, 'html'))

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(EMAIL, PASSWORD)
    message = msg.as_string()
    s.sendmail(EMAIL, toaddr, message)
    s.quit()
    print("[] Verified Email Sent")

@app.route("/note-accept",methods=['POST','GET'])
def noteAccept():
    if (request.method =='POST'):
        noteData = request.get_json()
        voterId = noteData['voterId']
        userId = noteData['userId']
        noteId = noteData['noteId']
        noteData = firestoreDb.collection('notes').document(noteId).get().to_dict()
        
        if  "verifiedBy" in noteData:
            if voterId in noteData["verifiedBy"]:
                return jsonify({"error":"user trying to accept again"}),400
            else:
                noteData["verifiedBy"].append(voterId)
        else:
            noteData["verifiedBy"]=[voterId]
        if len(noteData["verifiedBy"])==2:
            noteData['isAdminApproved']=True
            html = """<!DOCTYPE html>
            <html lang="en">
            <head></head>
            <body>
                <h1>Greetings from Notely</h1>
                <p>Your notes on """+noteData['subjectName']+""" got successfully verified.</p>
                <h4>Thank you</h4>
                <p>Regards,</p>
                <p>Team Notely.</p>
            </body>
            </html>
            """
            email = firestoreDb.collection('students').document(noteData['uId']).get().to_dict()['studentEmail']
            sendNoteVerifiedEmail(email,html)
        res = firestoreDb.collection('notes').document(noteId).update(noteData)
        return jsonify({"message":"Verification updated"}),200

@app.route("/note-reject",methods=['POST','GET'])
def noteReject():
    if (request.method =='POST'):
        noteData = request.get_json()
        voterId = noteData['voterId']
        userId = noteData['userId']
        noteId = noteData['noteId']
        noteData = firestoreDb.collection('notes').document(noteId).get().to_dict()
        
        if  "rejectedBy" in noteData:
            if voterId in noteData["rejectedBy"]:
                return jsonify({"error":"user trying to reject again"}),400
            else:
                noteData["rejectedBy"].append(voterId)
        else:
            noteData["rejectedBy"]=[voterId]
        if len(noteData["rejectedBy"])==2:
            noteData['isAdminApproved']=False
            html = """<!DOCTYPE html>
            <html lang="en">
            <head></head>
            <body>
                <h1>Greetings from Notely</h1>
                <p>Your notes on """+noteData['subjectName']+""" got rejected, kindly correct it and reupload it again.</p>
                <h4>Thank you</h4>
                <p>Regards,</p>
                <p>Team Notely.</p>
            </body>
            </html>
            """
            email = firestoreDb.collection('students').document(noteData['uId']).get().to_dict()['studentEmail']
            sendNoteVerifiedEmail(email,html)
        res = firestoreDb.collection('notes').document(noteId).update(noteData)
        return jsonify({"message":"Verification updated"}),200


@app.route("/get-all-notes",methods=['POST','GET'])
def getAllNotes():
    if request.method=='GET':
        docs = firestoreDb.collection('notes').where(u'isAdminApproved', u'==', True).stream()
        notesList=[]
        for doc in docs:
            notesList.append(doc.to_dict())
        return jsonify({"notes":notesList}),200
@app.route("/update-votes",methods=['POST','GET'])
def updateNotes():
    if request.method == 'POST':
        noteData = request.get_json()
        res = firestoreDb.collection('notes').document(noteData['noteId']).set({
            "upVotes":noteData["upVotes"],
            "downVotes":noteData["downVotes"]
        },merge=True)
        print(res)
        if (res):
            return jsonify({"message":"Vote updated"}),200
        else:
            return jsonify({"message":res}),400
        
if __name__ == "__main__":
    app.run(debug=False)


# flask run``