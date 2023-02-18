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

load_dotenv()
API_KEY = os.getenv('KEY')

cred = credentials.Certificate("secret_key.json")
firebase_admin.initialize_app(cred)
firestoreDb = firestore.client()

SCOPES = ['https://www.googleapis.com/auth/drive']


app = Flask(__name__)

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
                                      fields='id',supportsAllDrives=True).execute()

        print(F'[] File uploaded')
        return file.get("id")
    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None
    os.remove(temp.name)
    return file.get('id')

@app.route("/upload-note",methods=["POST","GET"])
def uploadNotes():
    if (request.method=='POST'):
        file = request.files['file']
        uploaddata = json.loads(request.form['data'])
        uId = uploaddata['uId']
        userType = uploaddata["userType"]
        temp = tempfile.NamedTemporaryFile(delete=False)
        file.save(temp.name)
        doc_ref  = firestoreDb.collection(userType+'s').document(uId)
        if doc_ref:
            doc = doc_ref.get().to_dict()
            folderId = doc["folderId"]
            fileId = uploadFile(service,temp,file.filename,folderId)
            if fileId:
                uploaddata["isAdminApproved"]=False
                uploaddata["fileId"]=fileId
                dbRes = firestoreDb.collection(uId).document(fileId).set(uploaddata)
                if dbRes:
                    return jsonify({"message":"File uploaded sucessfully" }),200
                else:
                    return jsonify({"error":"Error while uploading the file"}),500
            else:
                print("[] Error while uploading the file")
                return jsonify({"error":"Error while uploading the file"}),500
        else:
            print("[] Error while retreiving the document from firebase.")
            return jsonify({"error":"Error while retreving the document from firebase"}),500

@app.route("/note-accept",methods=['POST','GET'])
def noteAccept():
    if (request.method =='GET'):
        return "Thank you for accepting"
if __name__ == "main":
    app.run(debug=False)


# flask run