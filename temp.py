# import firebase_admin
# from firebase_admin import auth
# from firebase_admin import credentials
# from firebase_admin import firestore
# from firebase_admin.exceptions import FirebaseError
# import os
# from dotenv import load_dotenv
# import requests
# import json
# load_dotenv()
# API_KEY = os.getenv('KEY')

# cred = credentials.Certificate("secret_key.json")
# firebase_admin.initialize_app(cred)

# # signup_url = "https://identitytoolkit.googleapis.com/v1/accounts:signUp?key="+API_KEY
# # data =json.dumps({"email":"loganvk18@gmail.com","password":"123456","returnSecureToken":True})
# # res = requests.post(signup_url,data=data)
# # res=res.json()

# # if ("localId" in res):
# #     print("successfully created")
# # if ("error" in res):
# #     print(res["error"]["message"])

# # loginUrl = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key="+API_KEY
# # data =json.dumps({"email":"loganvk@gmail.com","password":"123456","returnSecureToken":True})
# # res = requests.post(loginUrl,data=data)
# # res=res.json()
# # print(res)

# import random

# firestoreDb = firestore.client()
# uId = 'zWK7QqUwKdZXYlvzWdyF0zNso0I3'

# docs = firestoreDb.collection(u'students').stream()
# userDict =dict()
# for doc in docs:
#     userDict[doc.id] = doc.to_dict()
# randomUsers=[]
# while len(randomUsers)<3:
#     choice = random.choice( list(userDict.keys()))
#     if choice not in randomUsers and choice!=uId:
#         randomUsers.append(choice)
# # print(randomUsers)
# print(userDict[randomUsers[0]])
# # username, emailid, file


a = [
    {'1osirGQvfN9iQEuGPFBD9wu4btHFzVjiJ': {'type': 'midsemester', 'link': 'https://docs.google.com/document/d/1osirGQvfN9iQEuGPFBD9wu4btHFzVjiJ/edit?usp=share_link&ouid=111827661461814112034&rtpof=true&sd=true'},
    '1atDmPxT4ihgpcjmYzwPnXvsdb6m5cB3C': {'type': 'midsemester', 'link': 'https://docs.google.com/document/d/1atDmPxT4ihgpcjmYzwPnXvsdb6m5cB3C/edit?usp=share_link&ouid=111827661461814112034&rtpof=true&sd=true'}, 
    '1qomyI0Mm30zJbW1NlP5gl2bfwk3C2JlQ': {'type': 'midsemester', 'link': 'https://docs.google.com/document/d/1qomyI0Mm30zJbW1NlP5gl2bfwk3C2JlQ/edit?usp=share_link&ouid=111827661461814112034&rtpof=true&sd=true'}
    }
    ]

print(a[0].keys())
# print(a)