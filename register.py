import requests
import PySimpleGUI as sg
import json
import webbrowser
import re

def getRegisterlink(credentials):
    return "https://www.strava.com/oauth/authorize?state=AUTHORIZE&redirect_uri=http%3A%2F%2Flocalhost&response_type=code&client_id=" + str(credentials.get("client_id")) + "&approval_prompt=auto&scope=activity%3Aread_all"

def requestToken (credentials, code):
    p = {
        "client_id": credentials.get("client_id"),
        "client_secret": credentials.get("client_secret"),
        "code": code,
        "grant_type": "authorization_code"
    }

    resp = requests.post("https://www.strava.com/oauth/token", data=p)
    print(resp.text)
    json.dump(json.loads(resp.text),open("tokens.json", "w"))


registerLayout = [
    [
        sg.Text("REGISTER"),
    ],
    [
        sg.Multiline("This Button will open a link in the web browser. Log into Strava. You will be asked to allow the application access to read your activities. Then you will be redirected to a localhost page which does not exist. Copy the URL of this localhost page into the following text input, and the registration will be complete", no_scrollbar=True, disabled=True, size=(50,10))
    ],
    [
        sg.Button("Open Browser", key="-REGISTER-"),
    ],
    [
        sg.Text("localhost URL:"),
        sg.Push()
    ],
    [
        sg.Input(key = "-URL-"),
        sg.Button("Submit", key = "-SUBMIT-")
    ]

]

def register():
    credentials = json.load(open("credentials.json"))
    registerWindow = sg.Window("Register",registerLayout, element_justification="center")
    

    while True: 
        event,_ = registerWindow.read()
        if event == "Exit" or event == sg.WINDOW_CLOSED:
            break
        elif event =="-REGISTER-":
            webbrowser.open(getRegisterlink(credentials))
        elif event == "-SUBMIT-":
            localhostUrl = registerWindow["-URL-"].get()
            code = re.search("code=([a-f0-9]+)", localhostUrl).group(1)
            print("Code: " + code)
            requestToken(credentials, code)
            break

if __name__ == "__main__":
    register()
