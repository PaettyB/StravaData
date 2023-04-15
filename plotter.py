import matplotlib.pyplot as plt
import matplotlib.dates as dt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

plot_colors = ["#1c5d99","#b75d69","#00cc99","#F56E2A", "#ffee88","#40bcd8","#462255"]

def setWindow(windowNew):
    global window
    window = windowNew

def draw_figure(figure_canvas_agg):
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


def updatePlot(fields, currentSport, dates_conv, display_type):
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
        values = list(map(lambda obj: fieldSelect(fields[i],  obj), currentSport))
        color = plot_colors[i]
        if i > 0:
            axi = ax.twinx()
            #offset the new axes by a gap
            axi.spines.right.set_position(("axes", 1.0 + (i-1)*0.1))
        axi.set_ylabel(fields[i])
        axi.yaxis.label.set_color(color)
        axi.tick_params(axis="y", colors=color)
        if display_type == 0:
            values = list(map(lambda obj: fieldSelect(fields[i],  obj, ignoreNone=False), currentSport))
            sc = axi.bar(dates_conv, values, color=color,width=2)
            axi.xaxis_date()
        elif display_type == 1:
            sc, = axi.plot_date(dates_conv, values, fmt=".", color=color)
            fig.autofmt_xdate()
        elif display_type == 2:
            sc, = axi.plot_date(dates_conv, values, fmt="-", color=color)
            fig.autofmt_xdate()
        fig.canvas.mpl_connect("button_press_event", lambda e: click(e, axi, sc, currentSport))
    draw_figure_w_toolbar(window["-CANVAS-"].TKCanvas, fig, window["-TOOLBAR-"].TKCanvas)


def updateActivitesInPlot(fields, activities, sport_type, display_type):
    currentSport = list(filter(lambda obj: obj['type'] == sport_type, activities))
    dates_conv = dt.date2num(list(map(lambda obj: obj['start_date'], currentSport)))
    updatePlot(fields, currentSport,dates_conv, display_type)
    if len(currentSport) > 0 :
        window["-KEY LIST-"].update(list(currentSport[0].keys()))
    else:
        window["-KEY LIST-"].update([])
        
    return currentSport,dates_conv