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

class Config:
    token = "ff84888cbc3d717524586b88f55e2373dd96e1e4f95ba0f2bdce1589ae6ad03c81dc97dd8d12230af0dbc"
    version = '5.131'
    
token = Bot(token="2057472245:AAHXiB2teJOWQa7CXwH0uLd8cJItn4YvD4A")


