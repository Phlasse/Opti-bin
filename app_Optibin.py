from tkinter import *
import os
from os.path import isfile, join
import time
import pandas as pd
import numpy as np
import optibin.fivebin
import matplotlib.pyplot as plt


################################################################################
##### Overall Layout ###########################################################
################################################################################
root = Tk()
root.title("Opti-Bin")
root.geometry("955x600")

head_frame = LabelFrame(root, text="Binning Tools", padx=90, pady=10)
head_frame.grid(row=0, column=0)

tool_frame = LabelFrame(root, text="Tool Konfiguration", padx=12, pady=10)
tool_frame.grid(row=1, column=0, pady=10, padx=10)

manual_frame = LabelFrame(root, text="Festlegen der Bin-Grenzen (bei manuellem Binning)", padx=57, pady=10)
manual_frame.grid(row=2, column=0, pady=10, padx=10)

execute_frame = LabelFrame(root, text="Aktionen", padx=106, pady=10)
execute_frame.grid(row=3, column=0)

result_frame = LabelFrame(root, text="Ergebnisse", padx=80, pady=10)
result_frame.grid(row=0, column=1, rowspan=3)

#### head frame - Tool Auswahlmenü #############################################


#create widgets
'''Interessant für später, wenn es mehrere Tools gibt'''

description = Label(head_frame, text="Bitte wähle hier das gewünschte Sortier-Tool aus.")

tool_choice = IntVar()
tool_choice.set("1")

#place widgets
description.pack()
Radiobutton(head_frame, text="Five-bin", variable=tool_choice, value=1).pack()
Radiobutton(head_frame, text="Weiteres noch nicht verfügbar", variable=tool_choice, value=2).pack()


#### Tool frame - Conf Auswahlmenü #############################################


#create functions & variables

'''def confirm_file_selection():
    data_conf_label = Label(tool_frame, text="Auswahl bestätigt", fg="green")
    data_conf_label.grid(row=2, column=1)
    return'''# temporär entfernt um zu testen, ob es überhaupt noch verwendet wird?!

files = [f for f in os.listdir("data/Input") if isfile(join("data/Input", f))]
file_choice = StringVar()
file_choice.set(files[0])
file_drop = OptionMenu(tool_frame, file_choice, *files)

feature_prompt = Label(tool_frame, text="Welches 5ive-Bin Feature soll ausgeführt werden?")

feature_5bin = IntVar()
feature_5bin.set("1")
Radiobutton(tool_frame, text="Schnelles Binning", variable=feature_5bin, value=1).grid(row=2, column=1)
Radiobutton(tool_frame, text="Iteratives Binning \n(empfohlen)", variable=feature_5bin, value=2).grid(row=3, column=1)
Radiobutton(tool_frame, text="Manuelles Binning", variable=feature_5bin, value=3).grid(row=4, column=1)


#create widgets

data_selection_prompt = Label(tool_frame, text="Wähle einen Datensatz aus:")

tolerance_prompt = Label(tool_frame, text="Welche Bin-Toleranz soll\n verwendet werden?[%]")
tolerance_input = Entry(tool_frame, width=25)
tolerance_input.insert(0, "2.5")


#place widgets
data_selection_prompt.grid(row=0, column=0)

file_drop.grid(row=0, column=1)

tolerance_prompt.grid(row=1, column=0)
tolerance_input.grid(row=1, column=1)
feature_prompt.grid(row=2, column=0)

#### Manuelle Binning Einstellungen Frame ################################################

#create functions & variables



#create widgets

lower_bin_prompt = Label(manual_frame, text="Gewünschte untere Bin-Grenze:")
upper_bin_prompt = Label(manual_frame, text="Gewünschte obere Bin-Grenze:")
bin_tolerance_prompt = Label(manual_frame, text="Gewünschte Bin-Toleranz [ABS]:")

lower_bin_input = Entry(manual_frame, width=25)
lower_bin_input.insert(0, "1.7")

upper_bin_input = Entry(manual_frame, width=25)
upper_bin_input.insert(0, "1.8")

bin_tolerance_input = Entry(manual_frame, width=25)
bin_tolerance_input.insert(0, "0.02")



#place widgets
lower_bin_prompt.grid(row=1, column=0)
upper_bin_prompt.grid(row=2, column=0)
bin_tolerance_prompt.grid(row=3, column=0)

lower_bin_input.grid(row=1, column=1)
upper_bin_input.grid(row=2, column=1)
bin_tolerance_input.grid(row=3, column=1)


##### Execute frame - Ausführung    ############################################

#create Functions and variables

def run_binning():
    tic = time.perf_counter()
    direction = file_choice.get()
    data = pd.read_csv("data/Input/"+direction).sort_values(by=['messdaten'])
    tolerance = float(tolerance_input.get())/100
    feature_choice = int(feature_5bin.get())

    if feature_choice == 1:
        Result, result_file_name = optibin.fivebin.mid_iterator(data, direction, tolerance, quick=True)
    elif feature_choice == 2:
        Result, result_file_name = optibin.fivebin.mid_iterator(data, direction, tolerance, quick=False)
    elif feature_choice == 3:
        Result, result_file_name = optibin.fivebin.specific_bin(data, direction, float(bin_tolerance_input.get()), float(lower_bin_input.get()), float(upper_bin_input.get()))
    else:
        pass
    toc = time.perf_counter()
    tictoc = round(toc-tic,0)
    time_label = Label(result_frame, text="Der Prozess dauerte "+str(round(tictoc,2))+" Sekunden\n").grid(row=1, column=0)
    if Result is None:
        error_label = Label(result_frame, text=result_file_name).grid(row=2, column=0)
        print(tkinter.__version__)

    else:
        success_label = Label(result_frame, text="Der Vorgang wurde erfolgreich beendet.\n", font=("calibri", 12), fg="green", padx=25).grid(row=0, column=0)
        lower_bin_label = Label(result_frame, text="Die untere Bin Grenze ist = "+str(round(min(np.array(Result.bin_sum)),4))).grid(row=2, column=0)
        upper_bin_label = Label(result_frame, text="Die obere Bin Grenze ist = "+str(round(max(np.array(Result.bin_sum)),4))).grid(row=3, column=0)
        variance_bin_label = Label(result_frame, text="Die maximale Varianz ist = "+str(round(max(np.array(Result.bin_dif)),4))).grid(row=4, column=0)
        save_label = Label(result_frame, text="Das Ergebnis wurde hier gespeichert:\n \n"+result_file_name).grid(row=5, column=0)
    return

def show_distplot():
    direction = file_choice.get()
    data = pd.read_csv("data/Input/"+direction).sort_values(by=['messdaten'])
    plt.hist(data.messdaten, 50)
    plt.show()
    return

#create widgets

execute_button = Button(execute_frame, text="Sortieren!", command=run_binning)
distribution_button = Button(execute_frame, text="Plotte Mess-Verteilung", command=show_distplot)

#place widgets

execute_button.pack(side="left", padx=10, pady=10)
distribution_button.pack(side="right", padx=10, pady=10)


#### Result frame - Ergebnisse #################################################

#ceate functions and variables


#create widgets
result_introduction_label = Label(result_frame, text="Hier werden Informationen zu den Ergebnissen erscheinen")


#place widgets
result_introduction_label.grid(row=0, column=0)


#################################################################
button_quit = Button(root, text="Programm Beenden", command=root.quit)

button_quit.grid(row=4, column=0, columnspan=2, pady=10)

#################################################################
# run the main "event loop
root.mainloop()
