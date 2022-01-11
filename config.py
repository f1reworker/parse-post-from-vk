import pyrebase

firebaseConfig = {
    'apiKey': "AIzaSyDxukMY1XocENNNPYfo8kzIfi37UFP5CG8",
  'authDomain': "vk-parse.firebaseapp.com",
  'databaseURL': "https://vk-parse-default-rtdb.europe-west1.firebasedatabase.app",
  'projectId': "vk-parse",
  'storageBucket': "vk-parse.appspot.com",
  'messagingSenderId': "519023209730",
  'appId': "1:519023209730:web:74b4c7fd5b7b532374e61b"
    }
firebase = pyrebase.initialize_app(firebaseConfig)
db= firebase.database()


a = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
print(a[:10])
