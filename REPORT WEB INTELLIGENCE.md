# REPORT WEB INTELLIGENCE

Scodeller Giovanni 864906



[TOC]



## Progetto

Progetto del corso Web Intelligence anno 2019/20 .

**Task**: Prevedere chi vincerà l'Open Australia 2020 simulando il torneo creando i singoli incontri. 

Il task del progetto è stato leggermente modificato, invece di prevedere chi vince l'Open Australia 2020, è stato creata un'analisi e dei modelli per simulare e prevedere il vincitore dell' Open del 2019.



## Introduzione

I dati utilizzati per il progetto erano facilmente reperibili scaricandoli dall'archivio [Tennis-Data](http://www.tennis-data.co.uk/ausopen.php) dove era possibile trovare tutti gli ATP dal 2001 al 2019 con descritti tutti i match disputati nel corso dell'anno.



## Early Data Analysis (EDA) 

Per una prima esplorazione dei dati prediamo in esempio l'anno sportivo 2017.

Notiamo che ogni entri del Dataset corrisponde ad una determinata partita giocata in quell'anno, in totale nel 2017 sono state disputate 2633 partite, per quanto riguarda le colonne notiamo che contengono vari dati che aiutano a descrivere gli incontri nello specifico.

Le feature possono essere divise in due categorie:

1. Quelle che descrivono i dati del torneo, dove possiamo osservare le colonne:

   - Date, ATP, Location, Tournament, Series, Court, Surface, Best Of

     Queste colonne descrivono principalmente tutte le caratteristiche di dove un determinato match è stato svolto ed il tipo di campo in cui si ha giocato.

   - Winner, Loser, WRank, LRank, WPts, LPts 

     Vengono descritte le informazioni relative ai giocatori che hanno giocato il match, i punti che hanno e la loro posizione nel ranking, è importante specificare che *viene già descritto chi ha vinto e chi ha perso*.

   - W1, L1, W2, L2, W3, L3, W4, L4, W5, L5, Wsets, Lsets, Comment

     Vengono descritti il numero di partite vinte per ogni set ed il numero totale di set ottenuti dal vincitore ed il perdente, inoltre viene descritto se il match è stato concluso regolarmente o per qualche altra ragione.

2. E quelle che descrivono tutte le quotazioni dei principali siti di scommesse.

### Prime considerazioni

- I dati non contengono valori difficili da lavorare, infatti sono stringhe o variabili numeriche. 
- Notiamo che per come i dati sono salvati non esiste una feature da prevedere poichè l'informazione che uno dei due giocatori ha vinto o perso viene descritta da due feature differenti.
- Nel dataset potrebbero esserci dei dati mancanti per errori di registrazione o non sono stati volutamente inseriti ( vedi set successivi ad una già avvenuta vittoria), bisognerà intervenire laddove i dati manchino inserendo i valori più opportuni per rendere il dataset coerente.



## Aggiunta della variabile "target"

Per affrontare il task di predizione del risultato di una partita di tennis abbiamo bisogno di una variabile che ci da un'informazione su chi di due giocatori è il vincitore.

Non esistendo già questa variabile, poichè nei dati forniti l'informazione viene descritta nelle colonne "Winner "e "Loser", abbiamo bisogno di crearla. La nuova feature aggiunta denominata "**target**" viene costruita nel seguente modo: "Contiene il valore 0 se in quel match vince il primo giocatore descritto, 1 se vince il secondo".

In questo modo però verrà aggiunta una sola colonna che contiene il valore 0 per tutte le partite dell'anno poichè il primo giocatore che viene descritto è **sempre** il vincitore.

Inoltre è stata creata la funzione ***generalFormatting***  utilizzata per cambiare il nome delle feature "Winner" e "Loser" in "Player1" e "Player2", vengono anche applicati altri metodi per formattare i dati. In generale le tecniche utilizzate sono:

- le colonne che contengono valori nulli vengono sistemati a criterio, se ad esempio un giocatore non ha punti in classifica entra con il minor numero di punti.

- Le colonne che contengono delle categorie, come "Court", "Surface" e "Best of" viene applicato il OneHotEncoding che crea tante feature  tante quante sono le categorie di quella feature assegnando valori 0 o 1.

  Esempio: "Court" contiene "Indoor" e "Outdoor", verranno create  "Court_Indoor" e "Court_Outdoor"

- Altre variabili come "Series" viene applicato il label enconding,  ovvero viene data un'etichetta numerica ad ogni classe della feature.



## Applicazione primo modello

Come primo approccio viene applicato un modello banale che servirà ad aver una soglia di accuratezza minima per i modelli successivi. Semplicemente la nostra previsione deciderà chi vince e chi perde in base alla loro posizione nel ranking, se "P1_Rank" è più basso viene predetto 0, altrimenti 1.

Prevedendo che vinca sempre il giocatore più forte otteniamo un'accuratezza di $\approx 0.65 \%$, che comunque non è uno scarso risultato per una previsione banale.

Inoltre è stato deciso di provare a testare un albero di decisione per vederne il suo comportamento, tecnica ci ha permesso di ottenere un aumento di precisione del modello di circa $\approx 6\%$ 



## Creazione di nuove feature

### Swap delle righe e "target" feature

Togliere l'informazione di chi vince e chi perde le partite purtroppo non basta per poter creare task di classificazione perchè così come sono formati i dati abbiamo solo una classe nella feature "target". Per questo è stata creata la funzione ***randomSwap*** per poter scegliere delle righe casuali ed invertire tutte le variabili di  "Player1" e "Player2" in modo da far comparire degli 1 nella feature "target" che ottengono il  significato "Player2 vince".

### Rateo vittorie fra giocatori rispetto l'anno precedente

Utilizzando la funzione ***addRateo*** verrà creata una matrice di giocatori X giocatori, dove le righe e le colonne sono l'unione degli atletiche hanno giocato l'anno precedente e l'anno del torneo che si vuole predirre. In questo modo grazie alle partite dell'anno precedente è possibile vedere quanto un giocatore è stato più forte o più scarso rispetto a tutti gli altri giocatori. Una cosa importante che viene applicata in questa matrice di giocatori X giocatori è una tecnica chiamata *smoothing* dei dati, consiste nell'aggiungere del rumore in modo tale da non avere eventi troppo rari o specifici, proponiamo un esempio: Se "Thompson J." contro "Dimitrov G." ha vinto 2 partite  su 2 giocate nell'anno precedente, avrà il 100% di vittoria su "Dimitrov G." e  "Thompson J." avrà lo 0% di vittoria e questo non è del tutto corretto. Se però aggiungiamo una vittoria ad entrambi i giocatori otterremo che "Thompson J." ha vinto 3  partite e "Dimitrov G." 1 partita, in questo modo otterremmo un rapporto 66% / 33% sulla probabilità di vittoria rendendo la feature più consistente.

### Vittorie  dei giocatori in un tipo di campo specifico

Dato un daframe ed l'anno a cui facciamo riferimento, viene creato un nuovo dataframe che contiene tutti gli atleti che hanno giocato dal 2001 all'anno precedente del torneo preso in analisi. In questo modo è possibile calcolare la bravura di un giocatore in un determinato tipo di campo, ne esistono di 3 categorie "Clay","Hard" e "Grass". Anche qui viene applicato lo *smoothing*  per i giocatori che non hanno mai giocato in un determinato tipo di campo o hanno iniziato a partecipare ai tornei nell'anno che viene analizzato. Tutto questo appena descritto viene effettuato dalla funzione ***addFieldWR***.



### Win Streak e Lose Streak dei giocatori

Tramite la funzione ***addPrevWin*** vengono aggiunte le informazioni di quante partite un giocatore sta vincendo di fila, ma anche quante ne sta perdendo, si pensa che un giocatore in forma è più propenso a vincere anche la partita successiva, si può ragionare analogamente anche per un giocatore che non essendo in forma è più propenso a perdere.



## Modelli di Supervised Learning

Prima dell'applicazione di qualsiasi modello sono state aggiunte le nuove feature precedentemente descritte ed inoltre vengono scartate le colonne che contengono informazioni sulle scommesse poiché quando andremo a simulare il torneo per determinare il vincitore dell'Open Australia non saranno dei dati disponibili dopo il primo Round. Inoltre i dati verranno divisi in train e test set, analogamente utilizzati per l'allenamento del modello ed il test per vedere i risultati ottenuti.

### Albero di decisione

Proviamo ad applicare un albero di decisione sui nuovi dati a cui sono state aggiunte le feature, è stato deciso di utilizzare come parametro di terminazione il raggiungimento di un determinato numero di foglie e notiamo che abbiamo un sostanziale aumento nella precisione sul test set del circa $\approx 10 \%$. Questo ci permette di dire che rispetto all'utilizzo delle feature di base, l'aggiunta di quelle che sono state create aiutano ad aumentare la precisione del modello e la descrizione dei dati.

### Ensemble Methods

A questo punto possiamo provare ad utilizzare dei metodi insiemistici applicati all'albero di decisione per vedere se possiamo migliorare ulteriormente la precisione del nostro modello.

La prima tecnica che proviamo ad applicare è il ***BAGGING*** esso ci permette di ridurre la varianza e notiamo che nonostante si aumenti il numero di modelli utilizzati otteniamo un miglioramento massimo del $\approx \%3$, arrivando quindi ad un accuracy score di $\approx 83\%$ , viene provato ad applicare anche il metodo di **BOOSTING** notando un guadagno simile a quello precedente.

#### Random Forest

Come ultimo modello viene provato ad applicare il metodo delle random forest per vedere se riusciamo a migliorare ulteriormente il nostro modello. Nonostante sia il metodo di previsione più complesso applicato otteniamo un aumento di precisione di un ulteriore $\approx 2 \%$.



### Recursive Feature Elimination (RFE)

A questo punto proviamo a vedere quali sono le $N$ più importanti per la costruzione del nostro modello di previsione.

 Se ad esempio scegliamo di selezionare le 6 feature più importanti possiamo notare che siano:

- P1_Pts
- P2_Pts
- P1_winningField
- P2_winningField
- P2_winningField 
- P2_losingField



## Simulazione del torneo

Per simulare il torneo è stata creata una funzione apposita chiamata ***tournamentSimulation*** essa prende in input il primo turno del torneo per poterne ricavare i giocatori e salvarli in un nuovo dataframe, il dataset del 2018 poiché servirà ad aggiornare il rateo tra due giocatori e come ultimo parametro un modello di decisione allenato che verrà utilizzato per prevedere l'esito degli incontri.

Il torneo viene costruito accoppiando i giocatori due a due per ogni turno del torneo, dopodiché viene utilizzato un modello di previsione per determinare il vincitore ed il perdente viene rimosso dalla lista dei giocatori, questo processo viene effettuato finché non rimarrà un solo giocatore che sarà il vincitore del torneo. 



## Considerazioni finali

Sono stati utilizzati diversi modelli di previsione in questo assigment e possiamo riassumerli nella seguente tabella:

| Modello                                           | Accuracy Score |
| ------------------------------------------------- | -------------- |
| Modello banale (Più forte vince)                  | 65 %           |
| Albero di Decisione (No feature aggiunte)         | 68 %           |
| Albero di Decisione ( Split  = Gini )             | 80 %           |
| Albero di Decisione ( Split  = Information Gain ) | 80 %           |
| Albero di Decisione con Bagging                   | 82 %           |
| Albero di Decisione con Boosting                  | 81 %           |
| Random Forest                                     | 85 %           |
| RFE                                               | 86 %           |

