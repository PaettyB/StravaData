import requests
import PySimpleGUI as sg
import json
import webbrowser
import re
from tkinter import filedialog
import shutil

config = json.load(open("config.json"))

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
    json.dump(json.loads(resp.text),open(config["tokenFile"], "w"))


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

credentialLayout = [
    [
        sg.Text("Application ID:"),
        sg.Push(),
        sg.Input(key = "-CLIENT_ID-")
    ],
    [
        sg.Text("Application Secret:"),
        sg.Push(),
        sg.Input(key = "-CLIENT_SECRET-")
    ],
    [
        sg.Multiline("To use this application, you need the Strava App ID and secret. To get this information, feel free to open a pull request on the Github page of this project!\n Alternatively, you can supply the Strava data yourself. It must be formatted in a .JSON file correctly.", no_scrollbar=True, disabled=True, size=(50,10))
    ],
    [
        sg.Button("Save Credentials", key="-SAVE-"),
        sg.Text("or"),
        sg.Button("Select File", key="-SELECT FILE-")
    ]
]

def inputCredentials():
    credWindow = sg.Window("Input Credentials", credentialLayout, element_justification="center")
    while True:
        event,values = credWindow.read()
        if event == "Exit" or event == sg.WINDOW_CLOSED:
            credWindow.close()
            return False
        elif event == "-SAVE-":
            id = credWindow["-CLIENT_ID-"].get()
            secret = credWindow["-CLIENT_SECRET-"].get()
            if id == "" or secret == "":
                sg.popup("Client ID and Secret must be supplied!")
            else:
                c = {
                    "client_id": int(id),
                    "client_secret": secret
                }
                json.dump(c, open(config["credentialsFile"], "w"))
                config["OfflineMode"] = False
                json.dump(config, open("config.json", "w"))
                credWindow.close()
                return True
        elif event == "-SELECT FILE-":
            path = filedialog.askopenfilename()
            if path == "":
                continue
            shutil.copyfile(path, config["activitiesFile"])
            config["OfflineMode"] = True
            json.dump(config, open("config.json", "w"))
            credWindow.close()
            return True


def register():
    credentials = json.load(open(config["credentialsFile"]))
    registerWindow = sg.Window("Register",registerLayout, element_justification="center")

    while True: 
        event,_ = registerWindow.read()
        if event == "Exit" or event == sg.WINDOW_CLOSED:
            registerWindow.close()
            return False
        elif event =="-REGISTER-":
            webbrowser.open(getRegisterlink(credentials))
        elif event == "-SUBMIT-":
            localhostUrl = registerWindow["-URL-"].get()
            code = re.search("code=([a-f0-9]+)", localhostUrl).group(1)
            print("Code: " + code)
            requestToken(credentials, code)
            registerWindow.close()
            return True

