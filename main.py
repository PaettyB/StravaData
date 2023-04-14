import json
import matplotlib.dates as dt
import PySimpleGUI as sg
import webbrowser
import fetch
import os
import sys
import plotter

bold_font = ("Arial", 12, "bold underline")

key_list_column= [
    [
        sg.Button("Update Activities", key="-FETCH-", expand_x=True, pad=(0,30))
    ],
    [
        sg.Radio("Bike",key="-BIKE-" , group_id=1, default=True, enable_events=True),
        sg.Radio("Run",key="-RUN-", group_id=1, enable_events=True),
        sg.Radio("Swim", key="-SWIM-", group_id=1, enable_events=True)
    ],
    [
        sg.Text("Keys", font=bold_font)
    ],
    [
        sg.Listbox(values= [],enable_events=True, select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED,size=(40,30), key="-KEY LIST-")
    ],
    [
        sg.Text("Display Type:")
    ],
    [
        sg.Button("Bars", key="-BARS-"),
        sg.Button("Scatter", key="-SCATTER-"),
        sg.Button("Line", key="-LINE-"),
        sg.Push(),
        sg.Button("Clear", key="-CLEAR-")

    ]
]

graph_column = [
    [
        sg.Text("Graph:", font=bold_font), 
        sg.Text("distance", size=(30,1), key="-DATA-"),
        sg.Text("Selected:", font = bold_font),
        sg.Text(size=(30,1), key="-ACTIVITY-", enable_events=True)
    ],
    [
        sg.Canvas(size=(1000, 800), key="-CANVAS-")
    ],
    [
        sg.Canvas(size=(400,42),key="-TOOLBAR-")
    ]
]

layout = [
    [
        sg.Column(key_list_column),
        sg.VerticalSeparator(),
        sg.Column(graph_column) 
    ]
]

if __name__ == "__main__":
    if not os.path.isfile("activities.json"):
        activities = fetch.updateLocalActivities()
    file = open("activities.json")
    activities = json.load(file)
    currentSport = list(filter(lambda obj: obj['type'] == "Ride", activities))
    dates = list(map(lambda obj: obj['start_date'], currentSport))
    dates_conv = dt.date2num(dates)

    window = sg.Window(title="Strava Data", layout=layout, finalize=True, location=(0,0), grab_anywhere_using_control=False)
    
    plotter.setWindow(window)
    
    window["-KEY LIST-"].update(values = list(currentSport[0].keys()))
    figure_canvas_agg = None
    display_type = 1
    fields = ["distance"]
    window["-KEY LIST-"].update(set_to_index = 3)
    plotter.updatePlot(fields,currentSport, dates_conv, display_type)

    while True: 
        event, values = window.read()
        if event == "Exit" or event == sg.WINDOW_CLOSED:
            file.close()
            break
        elif event == "-KEY LIST-":
            fields = values["-KEY LIST-"]
            if len(fields) > len(plotter.plot_colors):
                window["-KEY LIST-"].update(set_to_index = 3)
                fields = ["distance"]
            window["-DATA-"].update(fields)
            plotter.updatePlot(fields, currentSport, dates_conv, display_type)
        elif event == "-BARS-":
            display_type = 0
            plotter.updatePlot(fields, currentSport, dates_conv, display_type)
        elif event == "-SCATTER-":
            display_type = 1
            plotter.updatePlot(fields, currentSport, dates_conv, display_type)
        elif event == "-LINE-":
            display_type = 2
            plotter.updatePlot(fields, currentSport, dates_conv, display_type)
        elif event == "-ACTIVITY-":
            id = window["-ACTIVITY-"].get().split(" ")[0]
            if id != "":
                webbrowser.open("www.strava.com/activities/" + id)
        elif event == "-BIKE-":
            currentSport,dates_conv = plotter.updateActivitesInPlot(fields, activities, "Ride", display_type)
        elif event == "-RUN-":
            currentSport,dates_conv = plotter.updateActivitesInPlot(fields, activities, "Run", display_type)
        elif event == "-SWIM-":
            currentSport,dates_conv = plotter.updateActivitesInPlot(fields, activities, "Swim", display_type)
        elif event == "-CLEAR-":
            window["-KEY LIST-"].update(set_to_index = 3)
            fields = ["distance"]
            window["-DATA-"].update(fields)
            plotter.updatePlot(fields, currentSport, dates_conv, display_type)
        elif event == "-FETCH-":
            activities = fetch.updateLocalActivities()
            currentSport,dates_conv = plotter.updateActivitesInPlot(fields, activities, "Ride", display_type)
            window["-BIKE-"].reset_group()
            window["-BIKE-"].update(True)
    window.close()
