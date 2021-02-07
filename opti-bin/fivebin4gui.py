import pandas as pd
import numpy as np
import pyinputplus as pyip
import os
from os.path import isfile, join
import datetime
import time

currentDT = datetime.datetime.now()

def get_time():
    currentDT = datetime.datetime.now()
    return currentDT.strftime("%Y%m%d_%H%M_")

def get_bottom_up_bin_list(data, top=2, corridor=(1.75, 1.8)):
    ''' Diese Funktion fässt jeweis 5 Messungen so zusammen,
        dass der jeweilige Korridor und die max_dif eingehalten werden.

        Der Ansatz besteht darin, immer kleinere Tabellen aus 5 Daten zu
        erstellen die den Anforderungen gerecht werden und daraus eine
        Liste mit Tbellen zu erstllen. Die Ursprungsliste wird nach und nach
        abgebaut
    '''
    df = data
    bin_dfs=[]
    bin_neu = []
    tops = 0

    while len(df.messdaten)>0:  # solange noch mehr als 0 Messdaten vorhanden sind
            bin_neu = df[0:1] # nimm den kleinsten Wert der Tabelle
            df = df[df["serial#"] != bin_neu.iloc[-1]["serial#"]]#Beseitige diese Reihe aus der Ausgangstabelle

            # mit dem 1. niedrigen Wert wird nun geguckt, wie hoch die anderen 4 Werte durchschnittlich sein müssten,
            # sodass die aufsummierte 5er-Reihe mindestens die untere Korridorschwelle schafft.
            # mit dieser Information wird dann eine subtabelle erstellt ausschließlich mit Werten darüber
            # Diesen Vorgan wiederholt er bis er 5 Elemente voll hat.

            for i in range(4):
                ziel_avg = (corridor[0]-np.sum(bin_neu.messdaten))/(5-len(bin_neu.messdaten))
                bin_neu = pd.concat([bin_neu, df[df.messdaten > ziel_avg].head(1)], axis=0)
                df = df[df["serial#"] != bin_neu.iloc[-1]["serial#"]]
            bin_dfs.append(bin_neu)
            bin_neu=[]            # Da es mit diesem Algorithmus vorkommen kann, dass hiermit die obere Schwelle gerissen
            # werden kann, wird abwechselnd das gleiche von der oberen Schwelle ausgehend gemacht
            # "tops" ist die anzahl der mindestwechsel. tops kann in der Menge iteriert werden

            if tops < top:
                bin_neu = df.tail(1)
                df = df[df["serial#"] != bin_neu.iloc[-1]["serial#"]]
                for i in range(4):
                    ziel_avg = (corridor[1]-np.sum(bin_neu.messdaten))/(5-len(bin_neu.messdaten))
                    bin_neu = pd.concat([bin_neu, df[df.messdaten < ziel_avg].tail(1)], axis=0)
                    df = df[df["serial#"] != bin_neu.iloc[-1]["serial#"]]
                bin_dfs.append(bin_neu)
                bin_neu=[]
                tops+=1

    return bin_dfs

def create_bin_stats(list_of_bins):
    #set bin ids
    bin_no = []
    no = 1
    for i in range(len(list_of_bins)//5):
        for j in range(5):
            bin_no.append(no)
        no+=1
    list_of_bins["bin"] = bin_no
    bin_stats = list_of_bins.groupby(by="bin").agg({"messdaten":"sum"}).rename(columns = {"messdaten":"bin_sum"})
    bin_stats["bin_dif"] = list_of_bins.groupby(by="bin").agg({"messdaten":"max"}) - list_of_bins.groupby(by="bin").agg({"messdaten":"min"})
    list_of_bins = list_of_bins.merge(bin_stats, on="bin")
    return list_of_bins

def create_new_list(bin_list):
    ''' diese Funktion nimmt eine Liste aus listen und verkettet sie vertikal
        damit diese vernünftig ausgegeben werden kann'''
    start = bin_list[0]
    for i in bin_list[1:]:
        start=pd.concat([start, i], axis=0)
    cleaned_list = create_bin_stats(start)
    return cleaned_list

def get_input_stats(data, tolerance=0.028):
    ''' Diese Funktion nimmt den Eingangsdatensatz und bestimmt den größten und kleinsten
        Wert, den Durchschnittswert und die 5% max_dif (tolerance 2.5%)'''
    lim_upper = data["messdaten"].max()
    lim_lower= data["messdaten"].min()
    mean_df = data["messdaten"].mean()
    thresh_5_percent = data["messdaten"].mean()*(2*tolerance)
    mid_quantile = np.quantile(data["messdaten"], 0.5)
    return lim_upper, lim_lower, mean_df, thresh_5_percent, mid_quantile

def get_data():
    files = [f for f in os.listdir("../data/Input") if isfile(join("../data/Input", f))]
    files_dic = {}
    print(f"Folgende Daten wurden gefunden:\n")
    for num, i in enumerate(files):
        files_dic[num+1] = i
        print(f"[{num+1}] - {i}")
    choice = pyip.inputNum(f"\nWaehle eine Datei aus. (Index)\n")
    direction = files_dic[choice]
    data = pd.read_csv("../data/Input/"+direction)
    data = data.sort_values(by=['messdaten'])

    return data, direction

def get_tolerance():
    response_tol = pyip.inputYesNo(f"\nSoll eine Bin-Toleranz abweichend von (+/-) 2.5 % verwendet werden? (yes/no) \n") =="yes"
    if response_tol==True:
        tolerance = pyip.inputNum(f"\nEnter the percent")/100
    else:
        tolerance = 2.5/100
    return tolerance

def mid_iterator(data, file_direction, tolerance, quick=False):
    if quick == True:
        increment_no=10
    else:
        increment_no = 80

    stats = get_input_stats(data, tolerance)
    minimum = round(stats[0], 3)
    maximum = round(stats[1], 3)
    max_dif = round(stats[3], 3)
    mid_quantile = round(stats[4],3)
    initial_corridor = (5*mid_quantile-max_dif/4, 5*mid_quantile+max_dif/4)
    end_corridor = (5*mid_quantile-max_dif*10, 5*mid_quantile+max_dif*10)
    mid_down = [initial_corridor[0]]
    mid_up = [initial_corridor[1]]
    step_down = (initial_corridor[0]-end_corridor[0])/increment_no
    step_up = (end_corridor[1]-initial_corridor[1])/increment_no
    up_down_switch = int((len(np.array(data.messdaten)) / 5) / 2 - 1)

    for i in range(increment_no):
        mid_down.append(mid_down[-1] - step_down)
        mid_up.append(mid_up[-1] + step_up)
    corridor_pairs = []
    no_start = 1
    max_corridor_span = end_corridor[1]-end_corridor[0]
    print(corridor_pairs)
    for j in mid_down:
        for i in mid_up:
            corridor_pairs.append((round(j,3), round(i,3)))
    Result = "none"
    for pair in corridor_pairs:
        print(f"{no_start}/{len(corridor_pairs)} - Testing: {pair}")
        no_start +=1
        if pair[1] - pair[0] < max_corridor_span:
            for i in range(up_down_switch):
                result = create_new_list(get_bottom_up_bin_list(data, top=i, corridor=pair))
                if min(np.array(result.bin_sum)) >= pair[0] and max(np.array(result.bin_sum)) <= pair[1] and max(np.array(result.bin_dif)) <= max_dif:
                    max_corridor_span = max(np.array(result.bin_sum)) - min(np.array(result.bin_sum))
                    Result = result
                    print(f'results stored max corridor = {max_corridor_span} from {pair[0]} to {pair[1]}')
                    break
    if Result is "none":
        result_file_name = "Fivebin konnte kein Ergebnis erzielen."


    else:
        timestamp = get_time()
        result_file_name = "../data/Output/"+timestamp+file_direction.replace(".csv", "_result.csv")
        Result.to_csv(result_file_name)

    return Result, result_file_name

def specific_bin(data, file_direction, tolerance):
    stats = get_input_stats(data, tolerance=tolerance)
    max_dif = round(stats[3], 3)
    up_down_switch = int((len(np.array(data.messdaten)) / 5) / 2 - 1)


    while True:
        lower_thresh = pyip.inputNum(f"\nBitte gebe die untere Grenze an mit einem . als Dezimalseparator\n")
        upper_thresh = pyip.inputNum(f"\nBitte gebe die obere Grenze an mit einem . als Dezimalseparator\n")
        corridor = (lower_thresh, upper_thresh)
        print(f"\nDer eingegebene Korridor ist: {corridor}")
        response_corr = pyip.inputYesNo(f"\nStimmen die Werte? (yes/no) \n") == "yes"
        if response_corr is True:
            break
    Result = "none"
    for i in range(up_down_switch):
                result = create_new_list(get_bottom_up_bin_list(data, top=i, corridor=corridor))
                if min(np.array(result.bin_sum)) >= corridor[0] and max(np.array(result.bin_sum)) <= corridor[1] and max(np.array(result.bin_dif)) <= max_dif:
                    max_corridor_span = max(np.array(result.bin_sum)) - min(np.array(result.bin_sum))
                    Result = result

    if min(np.array(result.bin_sum)) >= corridor[0] and max(np.array(result.bin_sum)) <= corridor[1]:
        Result = result
        result_file_name = "../data/Output/"+file_direction.replace(".csv", "_result.csv")
        Result.to_csv(result_file_name)

    if Result is "none":
        print("Fivebin konnte kein Ergebnis erzielen.")

    else:
        timestamp = get_time()
        result_file_name = "../data/Output/"+timestamp+file_direction.replace(".csv", "_result.csv")
        Result.to_csv(result_file_name)

        print(f"\nDer Vorgang wurde beendet.")
        print(f'\nUntere Bin-Grenze= {min(np.array(Result.bin_sum))}')
        print(f'Obere Bin-Grenze= {max(np.array(Result.bin_sum))}')
        print(f'Maximale Varianz= {max(np.array(Result.bin_dif))}')

        print(f"\nDas Ergebnis wurde hier gespeichert: \n\n{result_file_name}\n")

    return True

def main():
    print("##############################\n")
    print(f"\nWillkommen beim Fivebin Binning Tool\n")
    data, file_direction = get_data()
    tolerance = get_tolerance()
    print(f"\n Folgende Features sind verfuegbar:\n")
    features = {1: "Iteratives Binning (Empfohlen)", 2 : "Schnelles Binning", 3 : "Bestimmtes Binning" , 9 : "Tool beenden"}

    choice = True
    while choice == True:
        for feature in features:
            print(f'[{feature}] - {features[feature]}')
        choice = pyip.inputNum(f"\nWelches Feature moechtest du verwenden?\n")
        tic = time.clock()
        if choice==1:
            choice = mid_iterator(data, file_direction, tolerance, quick=False)
            print(f'Der Prozess dauerte {time.clock() - tic} Sekunden')
        elif choice == 2:
            choice = mid_iterator(data, file_direction, tolerance, quick=True)
            print(f'Der Prozess dauerte {time.clock() - tic} Sekunden')
        elif choice ==3:
            choice = specific_bin(data, file_direction, tolerance)
            print(f'Der Prozess dauerte {time.clock() - tic} Sekunden')

        elif choice==9:
            choice = False
        else:
            print(f"Ich konnte das Programm nicht finden \n")
            continue
        print("Was moechtest du nun machen?\n")
    return True


if __name__ == '__main__':
    main()
