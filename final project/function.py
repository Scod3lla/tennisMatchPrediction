# LIBRERIE
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from pandas.api.types import CategoricalDtype



# CARICAMENTO DATI
# INPUT
# year -> anno da leggere
# RETURN ritorna il dataaset letto
def loadDataset(year):
    dataset_path = "../datasets/tennis/"+year+".xlsx"
    return pd.read_excel(dataset_path)


# Dato un dataframe ritorna i giocatori con un labelEncoding
# INPUT
# df -> dataframe da encodare
# RETURN i giocatori con un encoding numerico
def playEncode(df):
    playerList=set(df["Winner"]) | set(df["Loser"]) # Trovo tutti i giocatori singoli
    
    # Formattazione dei Giocatori
    playerEncode = {}
    for index, player in enumerate(playerList):
        playerEncode[player] = index
        
    return playerEncode


# Formattazione generale del dataset
# INPUT
# dfCopy -> dataframe da formattare
# playerEncode -> se passato fa encoding dei nomi
# RETURN un nuovo df formattato
def generalFormatting(dfCopy):
    df = dfCopy.copy()
    
    # Manage different NA column with different fill !
    # Fill NA
    df["WRank"].fillna(df["WRank"].max(), inplace = True)
    df["LRank"].fillna(df["LRank"].max(), inplace = True)
    
    df["WPts"].fillna(df["WPts"].max(), inplace = True)
    df["LPts"].fillna(df["LPts"].max(), inplace = True)

    df.fillna(0, inplace = True)

    # Cambio nome delle colonne Winner/Loser
    dictCol = {'Winner' :"Player1", 'Loser':'Player2', 'WRank':'P1_Rank', 'LRank':'P2_Rank', 'WPts':'P1_Pts', 'LPts':'P2_Pts',
       'W1':'P1_S1', 'L1':'P2_S1', 'W2':'P1_S2', "L2":'P2_S2', 'W3':'P1_S3', 'L3':'P2_S3', 'W4':'P1_S4', 'L4':'P2_S4', 'W5':'P1_S5', "L5":'P2_S5', 'Wsets':'P1_sets',
       'Lsets':'P2_sets', 'B365W':'P1_B365', 'B365L':'P2_B365', 'EXW':'P1_EX', 'EXL':'P2_EX', 'LBW':'P1_LB', 'LBL':'P2_LB', 'PSW':'P1_PS',
       'PSL':'P2_PS', 'MaxW':'P1_Max', 'MaxL':'P2_Max', 'AvgW':'P1_Avg', 'AvgL':'P2_Avg'}

    df.rename(columns=dictCol, inplace=True)
    
    
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
# INPUT
# df -> Dataframe da swapper
# randomNumber -> Numero di volte che lo swap viene effettuato
def randomSwap(df, randomNumber):
    swapCol=["Player1", "Player2"]
    for i in df.columns:
        if "P1" in i or "P2" in i:
            swapCol.append(i)

    maxRow = df.shape[0]
    print("Colonne che verranno swappate:")
    print(swapCol)
    for i in range(0,randomNumber):
        print("Random swap {}/{}".format(i+1,randomNumber), end="\r")
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
    
    print("")


# Crea una matrice di Giocatore X Giocatore segnando quante volte uno a vinto contro un altro
# INPUT
# df_old -> dataframe dell'anno precedente
# df_new -> dataframe dell'anno corrente
# RETURN un DF giocatore X giocatore
def playerDf(df_old, df_new):
    playerList=set(df_old["Player1"]) | set(df_old["Player2"]) | set(df_new["Player1"]) | set(df_new["Player2"]) # Trovo tutti i giocatori singoli
    
    newDf= pd.DataFrame(data = 0, index=playerList, columns=playerList) # Creo un dataframe per vedere chi vince con chi
    
    winLoseDf = df_old[["Player1","Player2"]] # Per popolarlo prendo chi vince e chi perde
    
    for index, row in winLoseDf.iterrows(): 
        # Doing +2 and +1 for the Player2 for "smoothing"
        newDf.loc[row["Player1"],row["Player2"]]+=2
        newDf.loc[row["Player2"],row["Player1"]]+=1
        
    return newDf



# calcola il rateo di vittoria di un giocatore, se i giocatori non hanno giocato è 0.5
# INPUT
# p1 -> giocatore1
# p2 -> giocatore2
# wl -> matrice Giocatore X Giocatore
# RETURN rateo
def rateo(p1, p2, wl):
    if wl.loc[p1, p2] == 0 and wl.loc[p2, p1] == 0:
        return 0.5
    else:
        return wl.loc[p1, p2] / (wl.loc[p1, p2]+wl.loc[p2,p1]) 

# aggiunge il rateo ai giocatori
# INPUT
# df_old -> dataframe dell'anno precedente
# df_new -> dataframe dell'anno corrente
def addRateo (df_old, df_new):
    playerMatrix = playerDf(df_old, df_new)
    df_new["P1_WinRateo"] = 0
    df_new["P2_WinRateo"] = 0

    # Per ogni riga aggiunge il rateo ai giocatori
    for index, row in df_new.iterrows():
        df_new.loc[index,"P1_WinRateo"] = rateo(row["Player1"],row["Player2"],playerMatrix)
        df_new.loc[index, "P2_WinRateo"] = rateo(row["Player2"],row["Player1"],playerMatrix)


# Crea un dataframe con i vincitori, perdenti e tipo di campo
# INPUT
# year -> anno a cui fermarsi
# RETURN un dataframe con tutti i tornei e il tipo di campo
def fieldWinLose (year):
    print("fieldWinLose")
    allCsv = pd.DataFrame(columns = ["Winner","Loser", "Surface"])
    
    for i in range(1,9):
        df = pd.read_excel("../datasets/tennis/200"+str(i)+".xls")
        df= df.loc[:,["Winner", "Loser","Surface"]]        
        frames = [allCsv, df]
        allCsv = pd.concat(frames, sort = False)
        print("Loaded dataset 200{}".format(i), end="\r")
    
    # change this depending on train year
    for i in range(0,year):
        df = pd.read_excel("../datasets/tennis/201"+str(i)+".xlsx")
        df= df.loc[:,["Winner", "Loser","Surface"]]        
        frames = [allCsv, df]
        allCsv = pd.concat(frames, sort = False)
        print("Loaded dataset 201{}".format(i), end="\r")
    
    print("")

    return allCsv


# Calcola il rateo di vittoria nel tipo di campo per ogni giocatore
# INPUT
# df -> dataframe di tutti gli anni precedenti
# now -> dataframe dell'anno corrente
# RETURN  dataframe del field win/lose rateo per tipo di campo
def OLDfieldWinLoseRateo(df, now, year = 9):
    playerList=set(df["Winner"]) | set(df["Loser"]) | set(now["Winner"]) | set(now["Loser"])
    print(len(playerList))
    subDf = pd.DataFrame(data = {"player":list(playerList), "hardWin": 1, "clayWin":1, "grassWin":1, "hardLose":1, "clayLose":1, "grassLose":1})
    i = 0
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

        print("Processing all player {}/{}".format(i+1,df.shape[0]), end="\r")
        i+=1
    
    print("")

    for index, row in subDf.iterrows():
        subDf.loc[index,"hardWin"] = row["hardWin"]/(row["hardWin"] + row["hardLose"])
        subDf.loc[index,"clayWin"] = row["clayWin"]/(row["clayWin"] + row["clayLose"])
        subDf.loc[index,"grassWin"] = row["grassWin"]/(row["grassWin"] + row["grassLose"])
        
        subDf.loc[index,"hardLose"] = row["hardLose"]/(row["hardWin"] + row["hardLose"])
        subDf.loc[index,"clayLose"] = row["clayLose"]/(row["clayWin"] + row["clayLose"])
        subDf.loc[index,"grassLose"] = row["grassLose"]/(row["grassWin"] + row["grassLose"])

    return subDf


# Calcola il rateo di vittoria nel tipo di campo per ogni giocatore
# INPUT
# df -> dataframe di tutti gli anni precedenti
# now -> dataframe dell'anno corrente
# RETURN  dataframe del field win/lose rateo per tipo di campo
def fieldWinLoseRateo(df, now):
    playerList=set(df["Winner"]) | set(df["Loser"]) | set(now["Winner"]) | set(now["Loser"])
    print(len(playerList))
    subDf = pd.DataFrame(data = {"player":list(playerList), "hardWin": 1, "clayWin":1, "grassWin":1, "hardLose":1, "clayLose":1, "grassLose":1})
    i = 0
    for player in playerList:
        #print(player)
        win  = df[df["Winner"] == player].loc[:,["Winner", "Loser", "Surface"]]
        #print(win)
    
        subDf.loc[subDf["player"] == player,"hardWin"] += win[win["Surface"] == "Hard"].shape[0]
        subDf.loc[subDf["player"] == player,"clayWin"] += win[win["Surface"] == "Clay"].shape[0]
        subDf.loc[subDf["player"] == player,"grassWin"] += win[win["Surface"] == "Grass"].shape[0]
        
        lose  = df[df["Loser"] == player].loc[:,["Winner", "Loser", "Surface"]]
        #print(lose)
        
        subDf.loc[subDf["player"] == player,"hardLose"] += lose[lose["Surface"] == "Hard"].shape[0]
        subDf.loc[subDf["player"] == player,"clayLose"] += lose[lose["Surface"] == "Clay"].shape[0]
        subDf.loc[subDf["player"] == player,"grassLose"] += lose[lose["Surface"] == "Grass"].shape[0]

        print("Processing all player {}/{}".format(i+1,len(playerList)), end="\r")
        i+=1

    print("")
    
    
    for index, row in subDf.iterrows():
        subDf.loc[index,"hardWin"] = row["hardWin"]/(row["hardWin"] + row["hardLose"])
        subDf.loc[index,"clayWin"] = row["clayWin"]/(row["clayWin"] + row["clayLose"])
        subDf.loc[index,"grassWin"] = row["grassWin"]/(row["grassWin"] + row["grassLose"])
        
        subDf.loc[index,"hardLose"] = row["hardLose"]/(row["hardWin"] + row["hardLose"])
        subDf.loc[index,"clayLose"] = row["clayLose"]/(row["clayWin"] + row["clayLose"])
        subDf.loc[index,"grassLose"] = row["grassLose"]/(row["grassWin"] + row["grassLose"])

    return subDf



# Aggiunge la colonna con il rateo in quel tipo di campo
# INPUT
# now -> dataframe dove vengono aggiunte le feature
# fwlr -> dataframe del field win/lose rateo
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

        print("Adding rateo {}/{}".format(index+1, now.shape[0]), end="\r")
    
    print("")


# Aggiunge la colonna di quanto quel giocatore ha vinto su quel tipo di campo
# Sto gia formattando gia il dataset
# INPUT
# now -> datraframe dove aggiungere le colonne
# year -> anno precedente a now  
# RETURN Dataframe formattato e con la feature aggiunta 
def addFieldWR (now, year):
    print("addFieldWR")
    copy =  now.loc[:,["Winner", "Loser","Surface"]]
    now = generalFormatting(now)
    fwlr = fieldWinLoseRateo(fieldWinLose(year),copy)
    addFieldWin(now, fwlr)

    return now




# Aggiunge la winStreak o loseStreak
# INPUT
# df_new -> Dataframe dell'anno corrente
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

        print("adding win streak / lose streak {}/{}".format( index+1, df_new.shape[0]), end="\r")

    print("")


# TOURNAMENT FUNCTION
# this set of function work with some tournament already exist (First turn)

# Prende tutti i giocatori
# INPUT
# tournament -> torneo dove prendere i giocatori
# RETURN dataframe con i giocatori ed i loro dati, le colonne di p1 e p2
def allPlayer(tournament):
    firstTurn = tournament[tournament["Round"] == 1]
    # Ricavare i giocatori
    p1Col = ["Player1"]
    for i in firstTurn.columns:
        if "P1" in i:
            p1Col.append(i) 

    p2Col = ["Player2"]
    for i in firstTurn.columns:
        if "P2" in i:
            p2Col.append(i) 
            
    allP1 = firstTurn[p1Col].reset_index(drop = True)
    
    #print(allP1)
    #print(allP1.shape[0])
    
    allP2 = firstTurn[p2Col].reset_index(drop = True)
    
    #print(allP2)
    #print(allP2.shape[0])
    
    noNameCol=["Player"]
    for i in p1Col:
        noNameCol.append(i.replace("P1_",""))
    
    noNameCol.remove("Player1")
    
    # print(noNameCol)
    
    # rinomino le colonne
    allP1.columns = noNameCol
    allP2.columns = noNameCol
    
    # allPlayer = pd.concat([allP1,allP2]).reset_index(drop = True)
    
    #Need to mantain the order o the player
    
    allPlayer = pd.DataFrame(columns = noNameCol)
    for i in range(0,64):
        index = i*2
        i1 = index
        i2 = index+1
        allPlayer.loc[i1] = allP1.loc[i]
        allPlayer.loc[i2] = allP2.loc[i] 
         
    #print(allPlayer)
    #print(allPlayer.shape[0])

    return allPlayer, p1Col, p2Col
    
    


# Crea la simulazione del torneo
# INPUT
# tournament -> torneo da simulare
# lastYear -> anno precendete
# tree -> decisionTree pre allenato
# RETURN vincitore del torneo
def tournamentSimulation(tournament, lastYear, tree):
    players, p1Col, p2Col = allPlayer(tournament)
    
    # colonne comuni
    nonPlayerCol = set(tournament.columns) - set(p1Col + p2Col)
    nonPlayerCol.remove("Tournament")
    #print(nonPlayerCol)
    
    p1Col.remove("Player1")
    p2Col.remove("Player2")
    
    #print(p1Col)
    #print(p2Col)
    
    tournamentSpec = tournament.loc[139,nonPlayerCol]

    turn = pd.DataFrame(columns=(list(nonPlayerCol) +p1Col + p2Col))
    
    for Round in range(1,8):
        
        print("Round", Round)
        
        # Creo il turno   
        turn = pd.DataFrame(columns=(list(nonPlayerCol) +p1Col + p2Col))
        for i in range(0, int(players.shape[0]/2)): 
            index = i*2
            p1 = index
            p2 = index+1

            # print(players.loc[p1,"Player"],players.loc[p2,"Player"])

            turn.loc[i,"Player1"] = players.loc[p1,"Player"]
            for col in p1Col:
                turn.loc[i,col] = players.loc[p1,(col.replace("P1_",""))]

            turn.loc[i,"Player2"] = players.loc[p2,"Player"]
            for col in p2Col:
                turn.loc[i,col] = players.loc[p2,(col.replace("P2_",""))]

            for col in nonPlayerCol:
                turn.loc[i,col] = tournament[col].tolist()[0]

            turn["Round"] = Round   

        addRateo(lastYear, turn)

        turn.drop("target", axis = 1, inplace = True)

        # lancio modello

        # faking decison tree with target
        #target = tournament[tournament["Round"] == Round]
        #target = target["target"].tolist()
        # print(target)  
    
        # print(turn.columns)
        
        target = tree.predict(turn.drop(["Player1", "Player2"], axis = 1))
    
        # sistemazione dati
        print(len(target))
        for res in range(0,len(target)):
            index = res*2
            p1 = index
            p2 = index+1

            #print(p1,p2)

            if target[res] == 0:
                players.drop(p2, inplace = True)
                players.loc[p1, "precWin"]+=1
                players.loc[p1, "precLose"] = 0
                
            else:
                players.drop(p1, inplace = True)
                players.loc[p2, "precWin"]+=1
                players.loc[p2, "precLose"] = 0


        players = players.reset_index(drop = True)
        #for index,aaa in players.iterrows():
        #   print(aaa["Player"])

    return players


# Crea una confusion matrix
def confusionMatrix(y_test, y_pred):
    from sklearn.metrics import confusion_matrix, classification_report
    import seaborn as sns
    import matplotlib.pyplot as plt

    conf_stat = confusion_matrix(y_true=y_test, y_pred=y_pred)

    fig, ax = plt.subplots(figsize=(5,5), tight_layout=True)
    sns.heatmap(conf_stat, annot=True, fmt=".3f", 
                linewidths=.5, square = True, 
                cmap = 'Blues_r',cbar=False,
                xticklabels=[0,1],
                yticklabels=[0,1]);
    ax.set_ylabel('True Label', fontsize=14);
    ax.set_xlabel('Predicted Label', fontsize=14);
