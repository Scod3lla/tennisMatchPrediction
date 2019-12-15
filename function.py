# LIBRERIE
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from pandas.api.types import CategoricalDtype


# CARICAMENTO DATI
def loadDataset(year):
    dataset_path = "../datasets/tennis/"+year+".xlsx"
    return pd.read_excel(dataset_path)


# Mi serve per sapere l'encoding dei giocatori 
# RITORNA i giocatori con un encoding numerico
def playEncode(df):
    playerList=set(df["Winner"]) | set(df["Loser"]) # Trovo tutti i giocatori singoli
    
    # Formattazione dei Giocatori
    playerEncode = {}
    for index, player in enumerate(playerList):
        playerEncode[player] = index
        
    return playerEncode


# Formattazione generale del dataset
# RITORNA un nuovo df formattato
def generalFormatting(dfCopy, playerEncode = 0):
    
    df = dfCopy.copy()
    
    # Cambio nome delle colonne Winner/Loser
    dictCol = {'Winner' :"Player1", 'Loser':'Player2', 'WRank':'P1_Rank', 'LRank':'P2_Rank', 'WPts':'P1_Pts', 'LPts':'P2_Pts',
       'W1':'P1_S1', 'L1':'P2_S1', 'W2':'P1_S2', "L2":'P2_S2', 'W3':'P1_S3', 'L3':'P2_S3', 'W4':'P1_S4', 'L4':'P2_S4', 'W5':'P1_S5', "L5":'P2_S5', 'Wsets':'P1_sets',
       'Lsets':'P2_sets', 'B365W':'P1_B365', 'B365L':'P2_B365', 'EXW':'P1_EX', 'EXL':'P2_EX', 'LBW':'P1_LB', 'LBL':'P2_LB', 'PSW':'P1_PS',
       'PSL':'P2_PS', 'MaxW':'P1_Max', 'MaxL':'P2_Max', 'AvgW':'P1_Avg', 'AvgL':'P2_Avg'}

    df.rename(columns=dictCol, inplace=True)
    
    if playerEncode != 0:
        df.replace({"Player1":playerEncode, "Player2":playerEncode}, inplace = True)
    
    # Fill NA
    df.fillna(0, inplace = True)
    
    # One Hot Encoding
    df = pd.get_dummies(df, columns = ["Court", "Surface", "Best of"])
    
    # Encoding Tipo torneo con peso
    df["Series"]=df["Series"].astype('category')
    cats_to_order = ["ATP250", "ATP500", "Masters 1000", "Masters Cup", "Grand Slam"]
    covered_type = CategoricalDtype(categories=cats_to_order, ordered=True)
    df['Series'] = df['Series'].cat.reorder_categories(cats_to_order, ordered=True)
    df["Series"] = df["Series"].cat.codes
    
    # Encoding Round Torneo con peso
    df["Round"]=df["Round"].astype('category')
    cats_to_order = ["Round Robin", "1st Round",'2nd Round','3rd Round','4th Round','Quarterfinals', 'Semifinals', 'The Final']
    covered_type = CategoricalDtype(categories=cats_to_order, ordered=True)
    df['Round'] = df['Round'].cat.reorder_categories(cats_to_order, ordered=True)
    df["Round"] = df["Round"].cat.codes
    
    # Rimozione colonne influenti
    df.drop(["Location", "ATP","Comment"], axis =1, inplace=True)
    
    # Encoding Nome tornei
    lb_make = LabelEncoder()
    df["Tournament"] = lb_make.fit_transform(df["Tournament"])
    df["target"] = 0
    
    return df


# Swap tra due valori
def swap (a,b):
    c=a
    a=b
    b=c
    return a,b

# Data un dataframe fa swap di colonne di righe random
# RANDOM SWAP "INPLACE"
def randomSwap(df, randomNumber):
    swapCol=["Player1", "Player2"]
    for i in df.columns:
        if "P1" in i or "P2" in i:
            swapCol.append(i)

    maxRow = df.shape[0]
    print(swapCol)
    for i in range(0,randomNumber):
        pos = np.random.randint(0,maxRow)
        for i in range(0, int(len(swapCol)/2)):
            index=i*2
            aa = swapCol[index]
            bb = swapCol[index+1]
            df.loc[pos,aa],df.loc[pos,bb] = swap(df.loc[pos,aa],df.loc[pos,bb])
            
        if df.loc[pos,"target"] == 0:
            df.loc[pos,"target"] = 1
        else:
            df.loc[pos,"target"] = 0


# Crea una matrice di Giocatore X Giocatore segnando quante volte uno a vinto contro un altro
# RITORNA un DF giocatore X giocatore
def playerDf(df_old, df_new):
    playerList=set(df_old["Player1"]) | set(df_old["Player2"]) | set(df_new["Player1"]) | set(df_new["Player2"]) # Trovo tutti i giocatori singoli
    
    newDf= pd.DataFrame(data = 0, index=playerList, columns=playerList) # Creo un dataframe per vedere chi vince con chi
    
    winLoseDf = df_old[["Player1","Player2"]] # Per popolarlo prendo chi vince e chi perde
    
    for index, row in winLoseDf.iterrows(): 
        # Doing +2 and +1 for the Player2 for "smoothing"
        newDf.loc[row["Player1"],row["Player2"]]+=2
        newDf.loc[row["Player2"],row["Player1"]]+=1
        
    return newDf



# Mi serve per calcore il rateo di vittoria di un giocatore, se i giocatori non hanno giocato è 0.5
def rateo(p1, p2, wl):
    if wl.loc[p1, p2] == 0 and wl.loc[p2, p1] == 0:
        return 0.5
    else:
        return wl.loc[p1, p2] / (wl.loc[p1, p2]+wl.loc[p2,p1]) 

# ADD RATEO OF PLAYER
def addRateo (df_old, df_new):
    playerMatrix = playerDf(df_old, df_new)
    df_new["P1_WinRateo"] = 0
    df_new["P2_WinRateo"] = 0

    for index, row in df_new.iterrows():
        df_new.loc[index,"P1_WinRateo"] = rateo(row["Player1"],row["Player2"],playerMatrix)
        df_new.loc[index, "P2_WinRateo"] = rateo(row["Player2"],row["Player1"],playerMatrix)


# FIELD VICTORY DF
# Ritorna un array con tutti i tornei e il tipo di campo
def fieldWinLose ():
    allCsv = pd.DataFrame(columns = ["Winner","Loser", "Surface"])
    
    for i in range(1,9):
        df = pd.read_excel("../datasets/tennis/200"+str(i)+".xls")
        df= df.loc[:,["Winner", "Loser","Surface"]]        
        frames = [allCsv, df]
        allCsv = pd.concat(frames, sort = False)
        
    for i in range(0,8):
        df = pd.read_excel("../datasets/tennis/201"+str(i)+".xlsx")
        df= df.loc[:,["Winner", "Loser","Surface"]]        
        frames = [allCsv, df]
        allCsv = pd.concat(frames, sort = False)
        
    
    return allCsv

# Calcola il rateo di vittoria
def fieldWinLoseRateo(df, now):
    playerList=set(df["Winner"]) | set(df["Loser"]) | set(now["Winner"]) | set(now["Loser"])
    print(len(playerList))
    subDf = pd.DataFrame(data = {"player":list(playerList), "hardWin": 1, "clayWin":1, "grassWin":1, "hardLose":1,
                                                             "clayLose":1, "grassLose":1})
    for index, row in df.iterrows():
        if row["Winner"] in playerList:
            subDf.loc[subDf["player"]==row["Winner"],"hardWin"]+=row["Surface"] == "Hard"
            subDf.loc[subDf["player"]==row["Winner"],"clayWin"]+=row["Surface"] == "Clay"
            subDf.loc[subDf["player"]==row["Winner"],"grassWin"]+=row["Surface"] == "Grass"
        elif row["Loser"] in playerList:
            subDf.loc[subDf["player"]==row["Loser"],"hardLose"]+=row["Surface"] == "Hard"
            subDf.loc[subDf["player"]==row["Loser"],"clayLose"]+=row["Surface"] == "Clay"
            subDf.loc[subDf["player"]==row["Loser"],"grassLose"]+=row["Surface"] == "Grass"
        else:    
            subDf.loc[subDf["player"]==row["Winner"],"hardWin"]+=1
            subDf.loc[subDf["player"]==row["Winner"],"clayWin"]+=1
            subDf.loc[subDf["player"]==row["Winner"],"grassWin"]+=1
            subDf.loc[subDf["player"]==row["Loser"],"hardLose"]+=1
            subDf.loc[subDf["player"]==row["Loser"],"clayLose"]+=1
            subDf.loc[subDf["player"]==row["Loser"],"grassLose"]+=1
            
        
    for index, row in subDf.iterrows():
        subDf.loc[index,"hardWin"] = row["hardWin"]/(row["hardWin"] + row["hardLose"])
        subDf.loc[index,"clayWin"] = row["clayWin"]/(row["clayWin"] + row["clayLose"])
        subDf.loc[index,"grassWin"] = row["grassWin"]/(row["grassWin"] + row["grassLose"])
        
        subDf.loc[index,"hardLose"] = row["hardLose"]/(row["hardWin"] + row["hardLose"])
        subDf.loc[index,"clayLose"] = row["clayLose"]/(row["clayWin"] + row["clayLose"])
        subDf.loc[index,"grassLose"] = row["grassLose"]/(row["grassWin"] + row["grassLose"])
        
    return subDf


def addFieldWin(now, fwlr):
    
    now["P1_winningField"] = 0
    now["P1_losingField"] = 0
    now["P2_winningField"] = 0
    now["P2_losingField"] = 0
    
    for index, row in now.iterrows():
        value1 = 0
        value2 = 0
        if now.loc[index, "Surface_Hard"] == 1:
            value1=fwlr[fwlr["player"] == row["Player1"]]["hardWin"].tolist()[0]
            value2=fwlr[fwlr["player"] == row["Player2"]]["hardWin"].tolist()[0]
            
        elif now.loc[index, "Surface_Grass"] == 1:
            value1=fwlr[fwlr["player"] == row["Player1"]]["grassWin"].tolist()[0]
            value2=fwlr[fwlr["player"] == row["Player2"]]["grassWin"].tolist()[0]

        elif now.loc[index, "Surface_Clay"] == 1:
            value1=fwlr[fwlr["player"] == row["Player1"]]["clayWin"].tolist()[0]
            value2=fwlr[fwlr["player"] == row["Player2"]]["clayWin"].tolist()[0]
    
    
        now.loc[index,"P1_winningField"] = value1
        now.loc[index,"P1_losingField"] = 1 - value1
        
        now.loc[index,"P2_winningField"] = value2
        now.loc[index,"P2_losingField"] = 1 - value2




# Add prev win streak
def addPrevWin(df_new):
    playerList=set(df_new["Player1"]) | set(df_new["Player2"])
    sub = pd.DataFrame(data = {"player":list(playerList), "P1_precWin":0, "P2_precWin":0, "P1_precLose":0, "P2_precLose":0})
    
    df_new["P1_precWin"], df_new["P2_precWin"], df_new["P1_precLose"], df_new["P2_precLose"] = [0,0,0,0]
    for index, row in df_new.iterrows():
        df_new.loc[index,"P1_precWin"] = sub[sub["player"] == row["Player1"]]["P1_precWin"].tolist()[0]
        df_new.loc[index,"P1_precLose"] = sub[sub["player"] == row["Player1"]]["P1_precLose"].tolist()[0]
        df_new.loc[index,"P2_precLose"] = sub[sub["player"] == row["Player2"]]["P2_precLose"].tolist()[0]
        df_new.loc[index,"P2_precWin"] = sub[sub["player"] == row["Player2"]]["P2_precWin"].tolist()[0]
            
        if row["target"] == 0:
            sub.loc[sub["player"]==row["Player1"],"P1_precWin"]+=1
            sub.loc[sub["player"]==row["Player1"],"P1_precLose"] = 0    
            sub.loc[sub["player"]==row["Player2"],"P2_precLose"]+=1
            sub.loc[sub["player"]==row["Player2"],"P2_precWin"] = 0
            
        else:
            sub.loc[sub["player"] == row["Player2"],"P2_precWin"] += 1
            sub.loc[sub["player"]==row["Player2"],"P2_precLose"] = 0
            sub.loc[sub["player"] == row["Player1"],"P1_precLose"] += 1
            sub.loc[sub["player"]==row["Player1"],"P1_precWin"] = 0


                
# Aggiunge la colonna, metodo da invocare, ritorna un df    
def addFieldWR (now):
    copy =  now.loc[:,["Winner", "Loser","Surface"]]
    now = generalFormatting(now)
    fwlr = fieldWinLoseRateo(fieldWinLose(),copy)
    addFieldWin(now, fwlr)

    return now