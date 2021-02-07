import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

data = pd.read_csv("data.csv")
data = data.sort_values(by=['messdaten'])
corridor=(1.75, 1.8)
max_dif = 0.02

def get_bins(X, top=4, corridor=(1.75, 1.8)):
    ''' Diese Funktion fässt jeweis 5 Messungen so zusammen,
        dass der jeweilige Korridor und die max_dif eingehalten werden'''
    df = X
    bin_dfs=[]
    bin_neu = []
    #df = df[df["serial#"] != df.iloc[0]["serial#"]]
    tops = 0
    while len(df.messdaten)>0:
            if bin_neu ==[]:
                bin_neu = df[0:1]
                df = df[df["serial#"] != bin_neu.iloc[-1]["serial#"]]#df[0:1]["serial#"]]
            for i in range(4):
                ziel_avg = (corridor[0]-np.sum(bin_neu.messdaten))/(5-len(bin_neu.messdaten))
                bin_neu = pd.concat([bin_neu, df[df.messdaten > ziel_avg].head(1)], axis=0)
                df = df[df["serial#"] != bin_neu.iloc[-1]["serial#"]]
            bin_dfs.append(bin_neu)
            bin_neu=[]
                #df = df[df["serial#"] != df[df.messdaten > ziel_avg][0:1].iloc[0]["serial#"]]
                #if len(bin_neu.messdaten) >4:
                 #   bin_dfs.append(bin_neu)
                  #  bin_neu=[]'''
            if tops < top:
                if bin_neu ==[]:
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

def create_bin_stats(X):
    #set bin ids
    bin_no = []
    no = 1
    for i in range(len(X)//5):
        for j in range(5):
            bin_no.append(no)
        no+=1
    X["bin"] = bin_no
    bin_stats = X.groupby(by="bin").agg({"messdaten":"sum"}).rename(columns = {"messdaten":"bin_sum"})
    bin_stats["bin_dif"] = X.groupby(by="bin").agg({"messdaten":"max"}) - X.groupby(by="bin").agg({"messdaten":"min"})
    X = X.merge(bin_stats, on="bin")
    return X

def create_new_list(bin_list):
    ''' diese Funktion nimmt eine Liste aus listen und verkettet sie vertikal
        damit diese vernünftig ausgegeben werden kann'''
    start = bin_list[0]
    for i in bin_list[1:]:
        start=pd.concat([start, i], axis=0)
    cleaned_list = create_bin_stats(start)
    return cleaned_list

def get_Input_stats(data, tolerance=0.025):
    ''' Diese Funktion nimmt den EIngangsdatensatz und bestimmt den größten und kleinsten
        Wert, den Durchschnittswert und die 5% max_dif (tolerance 2.5%)'''
    lim_upper =
    lim_loweer=
    mean_df
    thresh_5_percent
    pass




for i in range(10):
    result = create_new_list(get_bins(data, top=i, corridor=corridor))
    if min(np.array(result.bin_sum)) >= corridor[0] and max(np.array(result.bin_sum)) <= corridor[1] and max(np.array(result.bin_dif)) <= max_dif:
        print(f"Iteration {i}/10: was successful -> Result exported")
        result.to_csv("Ergebnis.csv")
        print(f' Untere Bin-Grenze= {min(np.array(result.bin_sum))}')
        print(f' Obere Bin-Grenze= {max(np.array(result.bin_sum))}')
        print(f' Maximale Varianz= {max(np.array(result.bin_dif))}')
        break
    else:
        print(f"Iteration {i}/10: could not sort")
        #print(f' Untere Bin-Grenze= {min(np.array(result.bin_sum))}')
        #print(f' Obere Bin-Grenze= {max(np.array(result.bin_sum))}')
        #print(f' Maximale Varianz= {max(np.array(result.bin_dif))}')
plt.hist((np.array(data.messdaten)*5), bins=33)
plt.show()
print(data.messdaten.describe())
