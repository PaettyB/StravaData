import json
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.figure
import matplotlib.dates as dt
import PySimpleGUI as sg
import numpy as np
import webbrowser

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


def draw_figure(figure_canvas_agg, figure):
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)
    return figure_canvas_agg

def draw_figure_w_toolbar(canvas, fig, canvas_toolbar):
    if canvas.children:
        for child in canvas.winfo_children():
            child.destroy()
    if canvas_toolbar.children:
        for child in canvas_toolbar.winfo_children():
            child.destroy()
    figure_canvas_agg = FigureCanvasTkAgg(fig, master=canvas)
    figure_canvas_agg.draw()
    toolbar = Toolbar(figure_canvas_agg, canvas_toolbar)
    toolbar.update()
    figure_canvas_agg.get_tk_widget().pack(side='right', fill='both', expand=1)


class Toolbar(NavigationToolbar2Tk):
    def __init__(self, *args, **kwargs):
        super(Toolbar, self).__init__(*args, **kwargs)


def click(event, ax, sc, activities):
    global activeEvent
    if event.inaxes == ax:
        cont, ind = sc.contains(event)
        if cont:
            activity = activities[ind["ind"][0]]
            print(activity["name"])
            window["-ACTIVITY-"].update(str(activity["id"]) +" - "+  activity["name"])
            window["-ACTIVITY-"].SetTooltip("Click to open Strava")
            window["-ACTIVITY-"].set_cursor("based_arrow_up")

def fieldSelect(field, obj,ignoreNone=True):
    val = obj.get(field)
    if(type(val) is object or type(val) is dict):
        return 0
    elif not ignoreNone and val is None:
        return 0
    else:
        return val
    
def updatePlot(fields, currentSport, display_type):
    fig = make_plot(fields, currentSport, display_type)
    draw_figure_w_toolbar(window["-CANVAS-"].TKCanvas, fig, window["-TOOLBAR-"].TKCanvas)


def make_plot(fields, activities, display_type):
    plt.figure(1)
    plt.clf()
    ax = plt.axes()
    axi = ax
    fig = plt.gcf()
    DPI = fig.get_dpi()
    
    fig.set_size_inches(1200 / float(DPI), 800 / float(DPI))
    #move the right end of the plot to the left
    fig.subplots_adjust(right=1.0 - (len(fields)) * 0.05)
    
    for i in range(len(fields)):
        values = list(map(lambda obj: fieldSelect(fields[i],  obj), activities))
        color = plot_colors[i]
        if i > 0:
            axi = ax.twinx()
            #offset the new axes by a gap
            axi.spines.right.set_position(("axes", 1.0 + (i-1)*0.1))
        axi.set_ylabel(fields[i])
        axi.yaxis.label.set_color(color)
        axi.tick_params(axis="y", colors=color)
        if display_type == 0:
            values = list(map(lambda obj: fieldSelect(fields[i],  obj, ignoreNone=False), activities))
            sc = axi.bar(dates_conv, values, color=color,width=1)
            axi.xaxis_date()
        elif display_type == 1:
            sc, = axi.plot_date(dates_conv, values, fmt=".", color=color)
            fig.autofmt_xdate()
        elif display_type == 2:
            sc, = axi.plot_date(dates_conv, values, fmt="-", color=color)
            fig.autofmt_xdate()
        fig.canvas.mpl_connect("button_press_event", lambda e: click(e, axi, sc, activities))
    return fig


bold_font = ("Arial", 12, "bold underline")
plot_colors = ["#1c5d99","#b75d69","#00cc99","#F56E2A", "#ffee88","#40bcd8","#462255"]

key_list_column= [
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
    global window
    global dates_conv
    
    file = open("activities.json")
    activities = json.load(file)
    currentSport = list(filter(lambda obj: obj['type'] == "Ride", activities))
    dates = list(map(lambda obj: obj['start_date'], currentSport))
    dates_conv = dt.date2num(dates)

    window = sg.Window(title="Strava Data", layout=layout, finalize=True, location=(0,0), grab_anywhere_using_control=False)
    window["-KEY LIST-"].update(values = list(currentSport[0].keys()))
    figure_canvas_agg = None
    display_type = 1
    fields = ["distance"]
    window["-KEY LIST-"].update(set_to_index = 3)
    fig = make_plot(fields, currentSport, display_type)
    draw_figure_w_toolbar(window["-CANVAS-"].TKCanvas, fig, window["-TOOLBAR-"].TKCanvas)

    while True: 
        event, values = window.read()
        if event == "Exit" or event == sg.WINDOW_CLOSED:
            break
        elif event == "-KEY LIST-":
            fields = values["-KEY LIST-"]
            if len(fields) > len(plot_colors):
                window["-KEY LIST-"].update(set_to_index = 3)
                fields = ["distance"]
            window["-DATA-"].update(fields)
            updatePlot(fields, currentSport, display_type)
        elif event == "-BARS-":
            display_type = 0
            updatePlot(fields, currentSport, display_type)
        elif event == "-SCATTER-":
            display_type = 1
            updatePlot(fields, currentSport, display_type)
        elif event == "-LINE-":
            display_type = 2
            updatePlot(fields, currentSport, display_type)
        elif event == "-ACTIVITY-":
            id = window["-ACTIVITY-"].get().split(" ")[0]
            if id != "":
                webbrowser.open("www.strava.com/activities/" + id)
        elif event == "-BIKE-":
            currentSport = list(filter(lambda obj: obj['type'] == "Ride", activities))
            dates_conv = dt.date2num(list(map(lambda obj: obj['start_date'], currentSport)))
            updatePlot(fields, currentSport, display_type)
        elif event == "-RUN-":
            currentSport = list(filter(lambda obj: obj['type'] == "Run", activities))
            dates_conv = dt.date2num(list(map(lambda obj: obj['start_date'], currentSport)))
            updatePlot(fields, currentSport, display_type)
        elif event == "-SWIM-":
            currentSport = list(filter(lambda obj: obj['type'] == "Swim", activities))
            dates_conv = dt.date2num(list(map(lambda obj: obj['start_date'], currentSport)))
            updatePlot(fields, currentSport, display_type)
        elif event == "-CLEAR-":
            window["-KEY LIST-"].update(set_to_index = 3)
            fields = ["distance"]
            window["-DATA-"].update(fields)
            updatePlot(fields, currentSport, display_type)
    window.close()
