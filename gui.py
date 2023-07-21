import PySimpleGUI as sg
from weathercalc import WeatherCalc

bt = {"size":(12,5),"font":("Helvetica")}
bw = {"background_color": "#FFFFFF", "text_color": "#000000"}

sg.theme('Dark Blue 2')

column_home = [[sg.Text("NOAA LCD Calculator", justification="center", font=("Helvetica", 30))], [sg.Text("", size=(1,2))],
               [sg.Button("Avg + Std Dev Daylight Temp", **bt), sg.Button("Windchills for Temps Sub-40", **bt), sg.Button("Most Similar\nDay", **bt)]]

layout_home = [[sg.VPush()],
              [sg.Push(), sg.Column(column_home,element_justification='c'), sg.Push()],
              [sg.VPush()]]

# form = sg.FlexForm('Home', default_button_element_size=(5,2), auto_size_buttons=False, grab_anywhere=False, size=(400, 300))
form = sg.FlexForm("Home", size=(500, 400))
form.Layout(layout_home)

def invalid_file_error(error_type):

    if error_type == "Date Error":
        message = "Please format your date as: 'YYYY-MM-DD'"
    elif error_type == "Date has no valid data":
        message = "Please input a date in the dataset"
    elif error_type == "File Error":
        message = "Please input a valid NOAA LCD CSV file"
    elif error_type == "Similar Day Files Error":
        message = "Please input valid NOAA LCD CSV files"
    elif error_type == "Similar Day Same File":
        message = "Please input two different files"
    else:
        return 0

    layout = [[sg.Text("ERROR!")], [sg.Text(message)], [sg.Text()], [sg.Push(), sg.Button("OK")]]
    error_window = sg.Window("ERROR!", layout, modal=True)
    while True:
        event, values = error_window.read()
        if event == sg.WINDOW_CLOSED or event=="OK":
            break
    
    error_window.close()
    return 1

def open_second_page(calc: WeatherCalc):
    layout = [[sg.Text("Daylight Temperature Average and Standard Deviation")], 
                [sg.Text("LCD Data File: ", size=(13,1)), sg.Input(key="file", **bw), sg.FileBrowse()],
                [sg.Text("YYYY-MM-DD:", size=(13,1)), sg.Input(key="date",  **bw)],
                [sg.Button("Calculate")],
                [sg.Text("")], #Spacer
                [sg.Text("Average:", size=(13,1)), sg.Input(key="avg_output",  **bw, readonly=True)],
                [sg.Text("Standard Dev:", size=(13,1)), sg.Input(key="std_dev_output",  **bw, readonly=True)]]
    window = sg.Window("Daylight Temp Average and Standard Deviation", layout, modal=True)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "Calculate":
            ret = calc.daylight_temp(window["file"].get(), window["date"].get())
            invalid_check = invalid_file_error(ret)
            if invalid_check == 0:
                window["avg_output"].update(str(ret[0])+"° F")
                window["std_dev_output"].update(str(ret[1])+"° F")

    
    window.close()

def open_third_page(calc: WeatherCalc):
    layout = [[sg.Text("Windchills When Temperature Below 40° F")], 
                [sg.Text("LCD Data File: ", size=(13,1)), sg.Input(key="file", **bw), sg.FileBrowse()],
                [sg.Text("YYYY-MM-DD:", size=(13,1)), sg.Input(key="date", **bw)],
                [sg.Button("Calculate")],
                [sg.Text("")], #Spacer
                [sg.Text("Windchills:", size=(13,1)), sg.Input(key="output", **bw, readonly=True)]]
    window = sg.Window("Windchills When Temperature Below 40° F", layout, modal=True)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "Calculate":
            ret = calc.windchills(window["file"].get(), window["date"].get())
            invalid_check = invalid_file_error(ret)
            if invalid_check == 0:
                ret_str = ""
                for chill in ret:
                    ret_str += str(chill) + "° F\n"

                window["output"].update(ret_str)
    
    window.close()

def open_fourth_page(calc: WeatherCalc):
    layout = [[sg.Text("Most Similar Day")], 
                [sg.Text("LCD Data File 1: ", size=(13,1)), sg.Input(key="file1", **bw), sg.FileBrowse()],
                [sg.Text("LCD Data File 2: ", size=(13,1)), sg.Input(key="file2", **bw), sg.FileBrowse()],
                [sg.Button("Calculate")],
                [sg.Text("")], #Spacer
                [sg.Text("Most Similar Day:", size=(13,1), ), sg.Input(key="output", **bw, readonly=True)]]
    window = sg.Window("Most Similar Day:", layout, modal=True)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "Calculate":
            if window["file1"].get() == window["file2"].get():
                invalid_file_error("Similar Day Same File")

            ret = calc.similar_day(window["file1"].get(), window["file2"].get())
            invalid_check = invalid_file_error(ret)
            if invalid_check == 0:
                window["output"].update(ret)   

    window.close()

    
while True:
    calc = WeatherCalc()
    event, values = form.read()
    if event == sg.WINDOW_CLOSED:
        break
    elif event == "Avg + Std Dev Daylight Temp":
        open_second_page(calc)
    elif event == "Windchills for Temps Sub-40":
        open_third_page(calc)
    elif event == "Most Similar\nDay":
        open_fourth_page(calc)

form.close()
    


    