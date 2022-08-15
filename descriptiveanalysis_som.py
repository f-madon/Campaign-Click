# -*- coding: utf-8 -*-
"""DescriptiveAnalysis_SOM.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1jyIUYl9ilzafxtSTyYAJZlRj7_JgC_ry

# Preparazione dei dati

## Import dei dati
"""

from google.colab import drive 
import pandas as pd
import re
from glob import glob
import numpy as np

from scipy.stats import pearsonr
import matplotlib.pyplot as plt
import seaborn as sns

drive.mount('/content/gdrive')
#La variabile verrà utilizzata dopo
suspicious_removed = False

!cp -av '/content/gdrive/My Drive/DS Lab - PROGETTO/Dataset aggregati' 'campaignClickDataset'

"""Recupero lisa dei files contenenti i dati"""

part_files = sorted(glob('campaignClickDataset/part*.csv'))

"""## Dataframe

Caricamento dati in un dataframe pandas
"""

df = pd.concat((pd.read_csv(file) for file in part_files), ignore_index=True)

df.dtypes

df.shape

"""Dal comando precedente le colonne totali risultano essere 1416"""

df.columns

"""## Cancellazioni

### Cancellazione delle colonne contenenti solo 0

Verifica colonne contenenti solo 0
"""

zeros_columns = []
for column in df:
    if (df[column] == 0.0).all():
      zeros_columns.append(column)
zeros_columns

"""Rimozione colonne contenenti solo 0 

"""

#removing columns containing only zeros
try:
  #df.drop(list(filter(lambda k: 'feelings' in k, zeros_columns)), axis = 1, inplace = True)
  df.drop(zeros_columns, axis = 1, inplace = True)
except:
  print('Probably the column has already been dropped in a previously execution. Continue')

#removing buy (it contains only zeros, removed by previous step)
#try:
#  df.drop('buy', axis = 1, inplace = True)
#except:
#  print('Probably the column has already been dropped in a previously execution. Continue')
df.shape

"""### Controlli vari

Verifica presenza duplicti iferiti allo user (identificato dalla colonna 'ad_form_id)
"""

df['ad_form_id'].duplicated().any()

"""Verifica presenza di righe con tutti valori a 0, escludendo la prima colonna"""

temp_df = df.drop('ad_form_id', axis=1)
temp_df[(temp_df != 0).all(1)]

#cancellazione temp_df, non più necessaria
del temp_df

"""### Cancellazione Categories2 e Categories3"""

# colonne che devo utilizzare (S perchè utilizzo dopo times1 e times2)
colonne = df.columns.to_numpy()
c2 = re.compile('^categories2+.*', re.IGNORECASE)
c3 = re.compile('^categories3+.*', re.IGNORECASE)
cat2 = []
cat3 = []

for v in colonne:
  if c2.search(v):
    #print(v)
    cat2.append(v)
  if c3.search(v):
    #print(v)
    cat3.append(v)

# elimino colonne 
df.drop(columns=cat2, inplace=True)
df.drop(columns=cat3, inplace=True)

ddd = list(df.columns)
for d in ddd: 
  print(d)

"""### Cancelazione admants e ad_form_id"""

AD = re.compile('^admants+.*', re.IGNORECASE)
admants = []

for v in df.columns:
  if AD.search(v):
    admants.append(v)

admants

df.drop(columns=admants, inplace=True)

# ad_form_id
df[df['ad_form_id'] < 0]

df.drop(columns='ad_form_id', inplace=True)

"""### Rimozione righe con suspicious=1

Estrazione righe con suspicious > 0, eliminazione dal dataframe originale 
Eliminazione colonna 'suspicious'
"""

if suspicious_removed == False:
  suspicious_df = df.loc[df['suspicious'] > 0]
  print('Initial df shape' + str(df.shape))
  df.drop(df[df.suspicious > 0].index, inplace=True)
  df.drop('suspicious', axis = 1, inplace = True)
print('Suspicious shape' + str(suspicious_df.shape))
print('Df shape after removal of suspicious > 0' + str(df.shape))
suspicious_removed = True

"""### Rimozione feelings, impression and time2"""

df.drop(columns='impressions', inplace=True)

colonne = df.columns.to_numpy()
t2 = re.compile('^time2+.*', re.IGNORECASE)
time2 = []

for v in colonne:
  if t2.search(v):
    time2.append(v)

df.drop(columns=time2, inplace=True)

colonne = df.columns.to_numpy()
f = re.compile('^feelings+.*', re.IGNORECASE)
feelings = []

for v in colonne:
  if f.search(v):
    feelings.append(v)

df.drop(columns=feelings, inplace=True)

"""### Aggiunta colonna `click_status`

"""

len(df[df['clicks'] != 0])

df[(df['clicks'] != 0) & (df['clicks'] != 1)]

df['click_status'] = np.where(df['clicks']>0, 'yes', 'no')
df[['clicks', 'click_status']]

len(df[df['click_status'] == 'yes' ])

#df.drop(columns='clicks', inplace=True)

"""## Normalizzazione

### Nornalizzazione colonne Categories
"""

# Colonne categories1
cat1 = re.compile('categories1_+.*', re.IGNORECASE)
cats1 = []
for label in colonne:
  occ = cat1.findall(label)
  if occ:
    cats1.append(occ[0])
  
# Calcolo somma
def somma_cat1(riga):
  sum = 0
  for cat in cats1:
    sum += riga[cat]
  return(round(sum, 1))

df['somma1'] = df.apply(somma_cat1, axis=1)

# Normalizzo le somme a 100
for cat in cats1:
  df[cat] = (df[cat] / df['somma1']) * 100
df['somma1'] = df.apply(somma_cat1, axis=1)

"""#### Rimozione righe con somma 'infinity'"""

df[(df['somma1'] != 100) & (df['somma1'].isnull())][['somma1']]

sum(df['somma1'].isnull())

df['somma1'].shape

indexNames = df[ (df['somma1'].isnull())].index
df.drop(indexNames, inplace=True)
df['somma1'].shape

df.drop(columns=['somma1'], inplace=True)

"""### Normalizzazione di 'Page length'"""

# stampa colonne
L = re.compile('^L+.*', re.IGNORECASE)
lung = []

for v in df.columns:
  if L.search(v):
    print(v)
    lung.append(v)

def somma_lung(riga):
  sum = 0
  for el in lung:
    sum += riga[el]
  return sum

df['somma'] = df.apply(somma_lung, axis=1)
df[['somma']]

from numpy import inf
sum(df['L00_50'] == inf) # infinity solo in L00_50

# NB inf + NaN = NaN

sum(df['somma'] == inf)

sum(df['somma'].isnull())

sum(df['somma'] != 100)

for l in lung:
  df[l] = (df[l] / df['somma']) * 100
df['somma'] = df.apply(somma_lung, axis=1)

df[['L00_50', 'L51_100', 'L101_250', 'L251_500', 'L501_1000', 'L1001_2500', 'L2501_5000', 'L5001_10000', 'L10001_more', 'somma']]

# rimozione coloumn 'somma'
df.drop(columns=['somma'], inplace=True)

"""### Normalizzazione di 'Time'"""

# colonne che devo utilizzare (S perchè utilizzo dopo times1 e times2)
colonne = df.columns.to_numpy()
t1 = re.compile('^time1+.*', re.IGNORECASE)
times1 = []

for v in colonne:
  if t1.search(v):
    print(v)
    times1.append(v)

# calcolo somma dei tempi (S)
df['sommat1'] = (df['time1_workday_morning'] + df['time1_workday_afternoon'] + df['time1_workday_evening'] + df['time1_workday_night'] +
                 df['time1_weekend_morning'] + df['time1_weekend_afternoon'] + df['time1_weekend_evening'] + df['time1_weekend_night'])

# Riscalo i tempi(2) in modo che somma sia 100 (S)
for t1 in times1:
  df[t1] = df[t1]/ df['sommat1']*100

df[times1].head(5)

# passaggi per controllo (arrotondo così non mi dà problemi se chiedo se è pari a 100)

df['sommat1'] = round(df['time1_workday_morning'] + df['time1_workday_afternoon'] + df['time1_workday_evening'] + df['time1_workday_night'] +
                 df['time1_weekend_morning'] + df['time1_weekend_afternoon'] + df['time1_weekend_evening'] + df['time1_weekend_night'], 2)

# controllo: tutte le somme sono a 100, tranne per i NaN

df[(df['sommat1'] != 100)][['sommat1']]

# elimino colonne contenenti la somma dei tempi (S)
df.drop(columns=['sommat1'], inplace=True)

"""## Unione variabili dummy"""

#Aggiunta colonne contenenti solo 0 per salvare i valoridelle variabili dummy
os_type = (np.zeros(df.shape[0], dtype=int))
browser_type = (np.zeros(df.shape[0], dtype=int))

#Aggiunta nuove colonne nel dataframe
df.insert(3, 'os_type', os_type)
df.insert(4, 'browser_type', browser_type)

#Verifica di 'non zero' in colonne os
os = ['android', 'bsd', 'ios', 'linux', 'osx', 'other', 'windows']
for nome in os:
  print(f'non zeros values os_{nome} = ' + str(len(df[df[f'os_{nome}']==1])))

#Rimozione colonna = 'os_ios'
df.drop(columns=['os_ios'], inplace=True)

#Verifica di 'non zero' in colonne os
browser = ['android', 'chrome', 'edge', 'firefox', 'ie', 'opera', 'other', 'safari', 'unknown']
for nome in browser:
  print(f'non zeros values browser_{nome} = ' + str(len(df[df[f'browser_{nome}']==1])))

for i in df.index:
  if df['os_bsd'].loc[i] == 1:
    df.at[i, 'os_type'] = 1
  elif df['os_linux'].loc[i] == 1:
    df.at[i, 'os_type'] = 2
  elif df['os_osx'].loc[i] == 1:
    df.at[i, 'os_type'] = 3
  elif df['os_windows'].loc[i] == 1:
    df.at[i, 'os_type'] = 4
  elif df['os_other'].loc[i] == 1:
    df.at[i, 'os_type'] = 5
  else:
    df.at[i, 'os_type'] = 0

for i in df.index:
  if df['browser_chrome'].loc[i] == 1:
    df.at[i, 'browser_type'] = 1
  elif df['browser_edge'].loc[i] == 1:
    df.at[i, 'browser_type'] = 2
  elif df['browser_firefox'].loc[i] == 1:
    df.at[i, 'browser_type'] = 3
  elif df['browser_ie'].loc[i] == 1:
    df.at[i, 'browser_type'] = 4
  elif df['browser_opera'].loc[i] == 1:
    df.at[i, 'browser_type'] = 5
  elif df['browser_safari'].loc[i] == 1:
    df.at[i, 'browser_type'] = 6
  elif df['browser_other'].loc[i] == 1:
    df.at[i, 'browser_type'] = 7
  elif df['browser_unknown'].loc[i] == 1:
    df.at[i, 'browser_type'] = 8
  else:
    df.at[i, 'browser_type'] = 0

#rimozione colonne ridondanti
df.drop(columns=['os_android', 'os_bsd', 'os_linux', 'os_osx', 'os_other', 'os_windows'], inplace=True)
df.drop(columns=['browser_android', 'browser_chrome', 'browser_edge', 'browser_firefox', 'browser_ie', 'browser_opera', 'browser_other', 'browser_safari', 'browser_unknown'], inplace=True)

"""## Unione colonne 'L'"""

df.shape

##Verifica di 'non zero' in colonne L
lenght = ['L00_50', 'L51_100', 'L101_250', 'L251_500', 'L501_1000', 'L1001_2500', 'L2501_5000', 'L5001_10000', 'L10001_more']
for nome in lenght:
  print(f'non zeros values {nome} = ' + str(len(df[df[f'{nome}']==0])))

L101_500 = df['L101_250'] + df['L251_500']

L501_more = df['L501_1000'] + df['L1001_2500'] + df['L2501_5000'] + df['L5001_10000'] + df['L10001_more']

df.insert(20, 'L101_500', L101_500)
df.insert(21, 'L501_more', L501_more)

zero = df['L00_50']+df['L51_100']+df['L101_500']+df['L501_more']

for riga in zero:
  if riga < 99:
    print(riga)

df.drop(columns=['L101_250', 'L251_500', 'L501_1000', 'L1001_2500', 'L2501_5000', 'L5001_10000', 'L10001_more'], inplace=True)

"""## NaN"""

df.fillna(df.mean(), inplace=True)

# calcolo somma dei tempi (S)
df['sommat1'] = (df['time1_workday_morning'] + df['time1_workday_afternoon'] + df['time1_workday_evening'] + df['time1_workday_night'] +
                 df['time1_weekend_morning'] + df['time1_weekend_afternoon'] + df['time1_weekend_evening'] + df['time1_weekend_night'])

# Riscalo i tempi(2) in modo che somma sia 100 (S)
# for t2 in times2:
#  df[t2] = df[t2]/ df['sommat2']*100

# Riscalo i tempi(1) in modo che somma sia 100 (S)
for t1 in times1:
  df[t1] = df[t1]/ df['sommat1']*100

# elimino colonne contenenti la somma dei tempi (S)
df.drop(columns=['sommat1'], inplace=True)

# passaggi per controllo (arrotondo così non mi dà problemi se chiedo se è pari a 100)

df['sommat1'] = round(df['time1_workday_morning'] + df['time1_workday_afternoon'] + df['time1_workday_evening'] + df['time1_workday_night'] +
                 df['time1_weekend_morning'] + df['time1_weekend_afternoon'] + df['time1_weekend_evening'] + df['time1_weekend_night'], 2)

# controllo: tutte le somme sono a 100

df[(df['sommat1'] != 100)][['sommat1']]

# elimino colonne contenenti la somma dei tempi (S)
df.drop(columns=['sommat1'], inplace=True)

# Controllo colonne nulle (qui per verificare che non ci siano eventuali somme nulle)
df[df.isnull().any(axis=1)]

"""## Colonne con soli 0

Verifica, dopo le modifiche precedenti, se ci sono colonne contenenti solo vlori=0
"""

zeros_columns1 = []
for column in df:
    if (df[column] == 0.0).all():
      zeros_columns1.append(column)
zeros_columns1

"""## Cambio del tipo di colonna"""

df.dtypes

df = df.astype({'os_type': 'category', 'browser_type': 'category', 'device_type': 'category', 'click_status': 'category'})

df.dtypes

"""# Analisi descrittiva dataset"""

df.head()

df.info()

df.shape

df.isnull().sum()

df.describe().to_excel("details.xlsx")

"""# SOM"""

!pip install minisom
from minisom import MiniSom
from sklearn.preprocessing import MinMaxScaler

df.columns

iterations = 1000
def computeSom(dataframe, size):
  #Scaling delel variabili
  sc = MinMaxScaler(feature_range = (0, 1))
  som_df = sc.fit_transform(dataframe)
  
  #calcolo som
  som = MiniSom(size, size, len(som_df[0]),
              neighborhood_function='gaussian',sigma=1.5,
              random_seed=1)

  som.pca_weights_init(som_df)
  som.train_random(som_df, iterations, verbose=True)
  return som

def showSom(som, size, feature_names, fig_size):
  W = som.get_weights()
  plt.figure(figsize=fig_size)
  for i, f in enumerate(feature_names):
      plt.subplot(len(feature_names)/3 + 1, 3, i+1)
      plt.title(f)
      plt.pcolor(W[:,:,i].T, cmap='coolwarm')
      plt.xticks(np.arange(size+1))
      plt.yticks(np.arange(size+1))
  plt.tight_layout()
  
  plt.savefig(feature_names[0] + '.pdf')
  plt.show()

feature_names = ['time1_workday_morning', 'time1_workday_afternoon', 'time1_workday_evening', 'time1_workday_night', 
               'time1_weekend_morning', 'time1_weekend_afternoon', 'time1_weekend_evening', 'time1_weekend_night','clicks']


print(feature_names)
som_df = df[feature_names]
som_df['clicks'] = df['clicks']
som_df

size = 25
som = computeSom(som_df, size)

showSom(som, size, feature_names, (16, 16))

feature_names = ['L00_50', 'L51_100', 'L101_500', 'L501_more','clicks']
som_df = df[feature_names]
som_df

som = computeSom(som_df, size)

showSom(som, size, feature_names, (16, 8))

feature_names = ['categories1_artandentertainment', 'categories1_automotive',
       'categories1_business', 'categories1_careers', 'categories1_education',
       'categories1_familyandparenting', 'categories1_finance',
       'categories1_foodanddrink', 'categories1_healthandfitness',
       'categories1_hobbiesandinterests', 'categories1_homeandgarden',
       'categories1_intentions', 'categories1_lawgovtandpolitics',
       'categories1_news', 'categories1_pets', 'categories1_realestate',
       'categories1_religionandspirituality', 'categories1_science',
       'categories1_shopping', 'categories1_society', 'categories1_sports',
       'categories1_styleandfashion', 'categories1_technologyandcomputing',
       'categories1_travel', 'categories1_uncategorized', 'clicks']
print(feature_names)
som_df = df[feature_names]
som_df

som = computeSom(som_df, size)

showSom(som, size, feature_names, (16, 32))