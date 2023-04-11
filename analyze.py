import json
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.figure
import matplotlib.dates as dt
import PySimpleGUI as sg
import numpy as np

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

file = open("activities.json")
activities = json.load(file)
print(len(activities))
bike = list(filter(lambda obj: obj['type'] == "Ride", activities))
dates = list(map(lambda obj: obj['start_date'], bike))
dates_conv = dt.date2num(dates)


def fieldSelect(field, obj):
    val = obj.get(field)
    if(type(val) is object or type(val) is dict):
        return 0
    else:
        return val

def make_plot(field, activities, display_type):
    
    plt.figure(1)
    plt.clf()
    ax = plt.axes()
    fig = plt.gcf()
    DPI = fig.get_dpi()
    # ------------------------------- you have to play with this size to reduce the movement error when the mouse hovers over the figure, it's close to canvas size
    fig.set_size_inches(1000 / float(DPI), 800 / float(DPI))
    
    values = list(map(lambda obj: fieldSelect(field,  obj), activities))
    if display_type == 0:
        ax.bar(dates_conv, values, width=1)
        ax.xaxis_date()
    elif display_type == 1:
        plt.plot_date(dates_conv, values, fmt=".")
        fig.autofmt_xdate()
    elif display_type == 2:
        plt.plot_date(dates_conv, values, fmt=".-")
        fig.autofmt_xdate()
    
    return fig



key_list_column= [
    [
        sg.Text("Keys")
    ],
    [
        sg.Listbox(values = list(bike[0].keys()), enable_events=True, size=(40,50), key="-KEY LIST-")
    ],
    [
        sg.Text("Display Type:")
    ],
    [
        sg.Button("Bars", key="-BARS-"),
        sg.Button("Scatter", key="-SCATTER-"),
        sg.Button("Line", key="-LINE-")
    ]
]

graph_column = [
    [sg.Text("Graph:"), sg.Text("distance", size=(30,1), key="-DATA-")],
    [sg.Canvas(size=(1000, 800), key="-CANVAS-")],
    [sg.Canvas(size=(1,42),key="-TOOLBAR-")]
]

layout = [
    [
        sg.Column(key_list_column, vertical_alignment="top"),
        sg.VerticalSeparator(),
        sg.Column(graph_column) 
    ]
]

window = sg.Window(title="Strava Data", layout=layout, finalize=True, location=(0,0))
figure_canvas_agg = None
display_type = 0
field = "distance"

while True: 
    event, values = window.read()

    if event == "Exit" or event == sg.WINDOW_CLOSED:
        break
    elif event == "-KEY LIST-":
        field = values["-KEY LIST-"][0]
        window["-DATA-"].update(field)
        fig = make_plot(field, bike, display_type)
        draw_figure_w_toolbar(window["-CANVAS-"].TKCanvas, fig, window["-TOOLBAR-"].TKCanvas)
    elif event == "-BARS-":
        display_type = 0
        fig = make_plot(field, bike, display_type)
        draw_figure_w_toolbar(window["-CANVAS-"].TKCanvas, fig, window["-TOOLBAR-"].TKCanvas)
    elif event == "-SCATTER-":
        display_type = 1
        fig = make_plot(field, bike, display_type)
        draw_figure_w_toolbar(window["-CANVAS-"].TKCanvas, fig, window["-TOOLBAR-"].TKCanvas)
    elif event == "-LINE-":
        display_type = 2
        fig = make_plot(field, bike, display_type)
        draw_figure_w_toolbar(window["-CANVAS-"].TKCanvas, fig, window["-TOOLBAR-"].TKCanvas)

window.close()
