import flask
import json
import pandas as pd
from flask_cors import CORS
import matplotlib.pyplot as plt

app = flask.Flask(__name__)
cors = CORS(app)

# Creo le stringhe per filtrare i lavori in base al loro stato, come specificato nel glossario, in ordine
str_prog = 'in programmazione|in progettazione' # In progettazione
str_esec = 'in esecuzione' # In esecuzione
str_term = 'terminato|lavori chiusi|in collaudo' # Terminato

'''Come primo grafico analizzeremo i Cantieri nei loro 3 Stati della Fibra FTTH divisi per ogni piano d'anno, 
quindi è normale che nel 2019 o 2020 non ci siano cantieri in esecuzione o in programmazione.

Piano d'anno, che si riferisce alla colonna 'Piano x (anno)' ('x' a seconda della tecnologia), è quando 
è stato emesso, in quale anno nello specifico, il programma specifico per quel cantiere e quindi anche il 
possibile inizio del cantiere. Nella mia Analisi ho deciso di togliere il 'possibile', e quindi di eguagliare 
l'anno di emissione del piano come l'anno di inizio dei laovori.
'''

df = pd.read_csv('./data/stato_lavori.csv', sep=';', encoding='UTF-8')

'''Dato che voglio portare la colonna 'Piano fibra (anno)' e 'Piano FWA (anno)' 
da float64 a int64, che riempire l'na come 0 per evitare errori nella riga dopo'''

df['Piano fibra (anno)'] = df['Piano fibra (anno)'].fillna(0)
df['Piano FWA (anno)'] = df['Piano FWA (anno)'].fillna(0)

df['Piano fibra (anno)'] = df['Piano fibra (anno)'].astype('int64')
df['Piano FWA (anno)'] = df['Piano FWA (anno)'].astype('int64')


@app.route("/cantieri_fibra", methods = ["POST"])
def getCantieriFibra():

    regione = flask.request.json["region"]

    if(regione == "Italia"):
        terminati = df[(df['Stato Fibra'].str.contains(str_term, na=False)) & (df['Fibra'] != 0)]['Piano fibra (anno)'].value_counts().sort_index().to_dict() # sort index gli ordina cronologicamente
        in_esecuzione = df[(df['Stato Fibra'].str.contains(str_esec, na=False)) & (df['Fibra'] != 0)]['Piano fibra (anno)'].value_counts().sort_index().to_dict() # to dict lo mette all'interno di un dizionario
        in_progettazione = df[(df['Stato Fibra'].str.contains(str_prog, na=False)) & (df['Fibra'] != 0)]['Piano fibra (anno)'].value_counts().sort_index().to_dict()
    
    else:
        terminati = df[(df['Regione'] == regione) &(df['Stato Fibra'].str.contains(str_term, na=False)) & (df['Fibra'] != 0)]['Piano fibra (anno)'].value_counts().sort_index().to_dict() # sort index gli ordina cronologicamente
        in_esecuzione = df[(df['Regione'] == regione) &(df['Stato Fibra'].str.contains(str_esec, na=False)) & (df['Fibra'] != 0)]['Piano fibra (anno)'].value_counts().sort_index().to_dict() # to dict lo mette all'interno di un dizionario
        in_progettazione = df[(df['Regione'] == regione) &(df['Stato Fibra'].str.contains(str_prog, na=False)) & (df['Fibra'] != 0)]['Piano fibra (anno)'].value_counts().sort_index().to_dict()
    
    cantieri_json = {
    'terminati': terminati,
    'in_esecuzione': in_esecuzione,
    'in_progettazione': in_progettazione
    }
    
    print(f"--> regione: {regione}")
    print(cantieri_json)
    
    return json.dumps(cantieri_json)

@app.route("/cantieri_regioni", methods=["POST"])
def getCantieriRegioni():
    
    regione = flask.request.json["region"]
    anno = int(flask.request.json["year"])
    connettività = flask.request.json["connectivity"]
    
    if connettività.lower() == 'fibra':
        stato_conn = 'Stato Fibra'
        anno_conn = 'Piano fibra (anno)'
    elif connettività.lower() == 'fwa':
        stato_conn = 'Stato FWA'
        anno_conn = 'Piano FWA (anno)'

    df_regione = df[df['Regione'] == regione]

    terminati = df_regione[(df_regione[stato_conn].str.contains(str_term, na=False)) & (df_regione[anno_conn] == anno)]['Provincia'].value_counts().sort_index().to_dict()
    in_esecuzione = df_regione[(df_regione[stato_conn].str.contains(str_esec, na=False)) & (df_regione[anno_conn] == anno)]['Provincia'].value_counts().sort_index().to_dict()
    in_progettazione = df_regione[(df_regione[stato_conn].str.contains(str_prog, na=False)) & (df_regione[anno_conn] == anno)]['Provincia'].value_counts().sort_index().to_dict()
        
    cantieri_json = {
        'terminati': terminati,
        'in_esecuzione': in_esecuzione,
        'in_progettazione': in_progettazione
    }
    
    print(f"--> regione: {regione}, anno: {anno}, connettività: {connettività}")
    print(cantieri_json)
    
    return  json.dumps(cantieri_json)



@app.route("/", methods = ["GET"])
def main():
    return {"Home": "working"}

if __name__ == "__main__":
    app.run(host="0.0.0.0")  