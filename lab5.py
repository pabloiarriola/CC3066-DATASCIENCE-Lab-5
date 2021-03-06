# -*- coding: utf-8 -*-
"""Lab5.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1FAvalsk0J0_z6uDH7QxNrLR5T4ogDDVx

# Laboratorio 5

---
Se necesita tener acceso los archivos de google drive para poder usar este código, aqui esta el link de compartir: <br>[Google Drive](https://drive.google.com/open?id=1qHCI8CdRZRUQJ9cHdwLO0OT4czG5c7r2) <br>

--- 
Tabla de contenido


*   Análisis Exploratorio

#Importaciones
"""

import pandas as pd
import numpy as np
import tensorflow as tf
from google.colab import files
import matplotlib.pyplot as plt
import re
import io 
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize
from nltk import ngrams
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import heapq
import operator
# Load library
from nltk.corpus import stopwords
import os
# You will have to download the set of stop words the first time
import nltk
nltk.download('stopwords')
stop_words = set(stopwords.words('english')) 
nltk.download('vader_lexicon')

"""### Conexión a Google Drive"""

!pip install -U -q PyDrive ## you will have install for every colab session
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from google.colab import auth
from oauth2client.client import GoogleCredentials
# 1. Authenticate and create the PyDrive client.
auth.authenticate_user()
gauth = GoogleAuth()
gauth.credentials = GoogleCredentials.get_application_default()
drive = GoogleDrive(gauth)

file_list = drive.ListFile({'q': "'1qHCI8CdRZRUQJ9cHdwLO0OT4czG5c7r2' in parents and trashed=false"}).GetList()
for file1 in file_list:
  print('title: %s, id: %s' % (file1['title'], file1['id']))

"""#Descargar el archivo de drive"""

GrammarandProductReviews = drive.CreateFile({'id': '1fGkPkrk96zg14OBcsGjFkOV8yJJpuJ_n'})
GrammarandProductReviews.GetContentFile('GrammarandProductReviews.csv')

dataset = pd.read_csv('GrammarandProductReviews.csv')
# dataset=pd.read_csv('GrammarandProductReviews.csv',sep='\t')

"""##Análisis Exploratorio

Lo primero que tenemos que ver es la fila donde tiene todos los nombres de los atributos para <br>
poder ver cuales son titulos de cada columna y poder ver a mas detalle las opciones que hay
"""

list(dataset)

"""#### Tabla: Columnas Importantes

| Columna        | Significado           |  Importancia
| :-------------: |:-------------:| -----:|
| review.title                             | Este es el titulo del review del usuario                               | Nos va a ayudar a distinguir el sentimineot  
| reviews.rating                       | La calificacion que el usuario le dio                                    |  Puntacion 
| review.reviewtext                 | Aqui es donde el usuario describe lo que penso de la pelicula | Esto es lo que mas se va a analisar 
| review.username                 | El usuario del que dio su opinion del producto                   | para saber quien es el que esta haciendo el review
| manufacturer                | El Productor del Producto                   | Para ver quien produjo ese producto y analisar el review del productor
"""

dataset['reviews.rating'].describe()

dataset = dataset.rename(columns={'reviews.text':'reviewtext'})
dataset = dataset.rename(columns={'reviews.title':'reviewtitle'})

dataset['reviewtext'].describe()

dataset['reviewtitle'].describe()

dataset['manufacturer'].describe()

"""###Limpieza de Datos"""

dataset.reviewtext

dataset.reviewtext = dataset.reviewtext.str.lower()
dataset.reviewtext.replace(regex=r'-', value=' ')
dataset.reviewtext.replace(regex=r'@', value=' ')
dataset.reviewtext.replace(regex=r'#', value=' ')
dataset.reviewtext.replace(regex=r'$', value=' ')
dataset.reviewtext.replace(regex=r'%', value=' ')
dataset.reviewtext.replace(regex=r'&', value=' ')
dataset.reviewtext.replace(regex=r'\.', value=' ')
dataset.reviewtext.replace(regex=r'\'', value='')
dataset.reviewtext.replace(regex=r'!', value=' ')

dataset.reviewtitle = dataset.reviewtitle.str.lower()
dataset.reviewtitle.replace(regex=r'-', value=' ')
dataset.reviewtitle.replace(regex=r'@', value=' ')
dataset.reviewtitle.replace(regex=r'#', value=' ')
dataset.reviewtitle.replace(regex=r'$', value=' ')
dataset.reviewtitle.replace(regex=r'%', value=' ')
dataset.reviewtitle.replace(regex=r'&', value=' ')
dataset.reviewtitle.replace(regex=r'\.', value=' ')
dataset.reviewtitle.replace(regex=r'\'', value='')
dataset.reviewtitle.replace(regex=r'!', value=' ')

dataset

#lowerYsub('GrammarandProductReviews.csv','GrammarandProductReviews2.csv')

"""###Quitar Stopwords"""

dataset['reviewtext'] = dataset['reviewtext'].astype(str)

print(stop_words)

dataset['reviewtext']

dataset['reviewtext'] = dataset['reviewtext'].astype(str)
dataset['reviewtitle'] = dataset['reviewtitle'].astype(str)

dataset['reviewtext'] = dataset['reviewtext'].str.split(' ').apply(lambda x: ' '.join(k for k in x if k not in stop_words))
dataset['reviewtitle'] = dataset['reviewtitle'].str.split(' ').apply(lambda x: ' '.join(k for k in x if k not in stop_words))

print (dataset['reviewtext'])

"""#### Las palabras que mas se repiten"""

palabrasMasComunes = {}

def word_count(str, dictionary):
  for word in str.split():
    if word in dictionary:
      dictionary[word] += 1
    else:
      dictionary[word] = 1
  return dictionary

for row in dataset.reviewtext.values:
    if type(row) == str:
      palabrasMasComunes = word_count(row, palabrasMasComunes)

"""###Histograma"""

def keyInOrder(listName, number):
  keys = list(sorted(listName, key=listName.__getitem__, reverse=True))
  keys = keys[:number]
  firstFew = {x:listName[x] for x in keys}
  return firstFew

palabrasOrdenadas = {}

for key, value in sorted(palabrasMasComunes.items(), key=operator.itemgetter(1), reverse=True):
  palabrasOrdenadas[key] = int(value)

keys = keyInOrder(palabrasOrdenadas, 10)

plt.bar(keys.keys(), keys.values(), color='b')
plt.title("Palabras Mas Comunes")

"""## Clasificador de Palabras"""



#Funcion que devuelve la clasificacion del review por medio de la cantidad de
#palabras positivas, negativas y neutras.
def clasificador(rev):
  sid = SentimentIntensityAnalyzer()
  pos_list=[]
  neu_list=[]
  neg_list=[]
  for word in rev.split():
    if (sid.polarity_scores(word)['compound']) >= 0.5:
        pos_list.append(word)
    elif (sid.polarity_scores(word)['compound']) <= -0.5:
        neg_list.append(word)
  resultado = "Neutro" 

#   print ("pos_list: %d  <==> %d  :neg_list" % (len(pos_list), len(neg_list)))

  if len(pos_list)<len(neg_list) and len(pos_list) == 0:
    resultado = "Altamente Negativo"
  if len(pos_list)>len(neg_list) and len(neg_list) == 0:
    resultado = "Altamente Positivo"
  if len(pos_list)<len(neg_list) and len(pos_list) > 0:
    resultado = "Levemente Negativo"
  if len(pos_list)>len(neg_list) and len(neg_list) > 0:
    resultado = "Levemente Positivo"
   
#   print("resultado: %s" % resultado)
  
  return (resultado)

dataset['resultado'] = 'Neutro'

for index, row in dataset.iterrows():
   dataset.loc[index,'resultado'] = clasificador(row['reviewtext'])

dataset['resultado']

"""#### Los Mejores Productos"""

# @params tiene que utilizar un dataset ya prechequiado con los valores que se quiere para aumentar la velocidad
def addPointsToDictionary(dictionaryOfPoints, columnName, givenDataset, pointsGiven):
  for index, row in givenDataset.iterrows():
    if row[columnName] in dictionaryOfPoints:
      dictionaryOfPoints[row[columnName]] += pointsGiven
    else:
      dictionaryOfPoints[row[columnName]] = pointsGiven
  return dictionaryOfPoints

datasetAltamentePositive = dataset.loc[dataset['resultado'] == "Altamente Positivo"]

datasetLevementePositive = dataset.loc[dataset['resultado'] == "Levemente Positivo"]

puntajePorProducto = {}

"""##### Los que tienen levemenete positivos tienen 1 punto y los de Altamente positivos son 2"""

puntajeLevementePos = 1
puntajeAltamentePos = 2

"""Primero vamos a buscar el nombre de producto que se encuentra en la columna 'name'"""

productoColumna = 'name'

"""Se agregan los puntos de altamente positivo"""

puntajePorProducto = addPointsToDictionary(puntajePorProducto, productoColumna, datasetAltamentePositive, puntajeAltamentePos)

"""Se agregan los puntos de levemente positivo"""

puntajePorProducto = addPointsToDictionary(puntajePorProducto, productoColumna, datasetLevementePositive, puntajeLevementePos)

print (puntajePorProducto)

puntajeProductoOrdenado = {}

for key, value in sorted(puntajePorProducto.items(), key=operator.itemgetter(1), reverse=True):
  puntajeProductoOrdenado[key] = int(value)

# sorted(palabrasMasComunes.items(), key=operator.itemgetter(1), reverse=True)
print(puntajeProductoOrdenado)

keys = keyInOrder(puntajeProductoOrdenado, 10)

"""## Los Mejores 10 Productos"""

c = 1
print("Top 10 mejores productos")
for key, value in keys.items():
  print ("%d: %s: Con %s puntos positivos" % (c, key, value))
  c += 1

"""#### Lo mismo pero ahora para los peores productos"""

datasetAltamentNegativo = dataset.loc[dataset['resultado'] == "Altamente Negativo"]

datasetLevementeNegativo = dataset.loc[dataset['resultado'] == "Levemente Negativo"]

puntajePeorProducto = {}

puntajePeorProducto = addPointsToDictionary(puntajePeorProducto, productoColumna, datasetAltamentNegativo, puntajeAltamentePos)

puntajePeorProducto = addPointsToDictionary(puntajePeorProducto, productoColumna, datasetLevementeNegativo, puntajeLevementePos)

puntajeProductoOrdenado = {}

for key, value in sorted(puntajePeorProducto.items(), key=operator.itemgetter(1), reverse=True):
  puntajeProductoOrdenado[key] = int(value)

keys = keyInOrder(puntajeProductoOrdenado, 10)

"""## Los Peores 10 productos"""

c = 1
print("Top 10 Peores Productos")
for key, value in keys.items():
  print ("%d: %s: Con %s puntos negativos" % (c, key, value))
  c += 1

"""#### Consiguiendo los distintos reviews de producto por usuarios"""

datasetDistinctUserConProduct = dataset.drop_duplicates(dataset[['reviews.username','name']])

dictionaryUsers = {}
columnaDeUserName = 'reviews.username'
# dictionaryOfPoints, columnName, givenDataset, pointsGiven):
dictionaryUsers = addPointsToDictionary(dictionaryUsers, columnaDeUserName, datasetDistinctUserConProduct, 1)

usernameOrdenado = {}

for key, value in sorted(dictionaryUsers.items(), key=operator.itemgetter(1), reverse=True):
  usernameOrdenado[key] = int(value)

keys = keyInOrder(usernameOrdenado, 10)

"""## Top 10 Usuarios con mayor distintos reviews"""

c = 1
print("Top 10 Usuarios con Distintos Reviews")
for key, value in keys.items():
  print ("%d: %s: Con %s reviews en diferentes productos" % (c, key, value))
  c += 1

"""##### Usuarios con mayor y menor puntaje de positivos o negativos"""

userDicitonaryConPositivos = {}
usersDictionaryConNegativos = {}

# aqui vamos a conseguir todos las veces que el usuario a puesto algo positivo
userDicitonaryConPositivos = addPointsToDictionary(userDicitonaryConPositivos, columnaDeUserName ,datasetAltamentePositive, 1)
userDicitonaryConPositivos = addPointsToDictionary(userDicitonaryConPositivos, columnaDeUserName ,datasetLevementePositive, 1)
# ya que tenemos los positivos hacemos lo mismo con los negativos
usersDictionaryConNegativos = addPointsToDictionary(usersDictionaryConNegativos, columnaDeUserName ,datasetAltamentNegativo, 1)
usersDictionaryConNegativos = addPointsToDictionary(usersDictionaryConNegativos, columnaDeUserName ,datasetLevementeNegativo, 1)
# ya que tenemos los puntajes por usuario hay que sacar el porcentaje de que tan positivos o negativos son sus reviews
userPorcentajeDeReview = {}
userPorcentajeDeReviewNeg = {}

def userDicitionaryAddPoints(userDictionaryPos, userDictionaryNeg , newDictionary):
  for key, value in userDictionaryPos.items():
    if key in userDictionaryNeg:
        newDictionary[key] = (value / (value + userDictionaryNeg[key]) ) * 100
  return newDictionary

userPorcentajeDeReview = userDicitionaryAddPoints(userDicitonaryConPositivos, usersDictionaryConNegativos, userPorcentajeDeReview)
puntajeProductoOrdenado = {}

for key, value in sorted(userPorcentajeDeReview.items(), key=operator.itemgetter(1), reverse=True):
  puntajeProductoOrdenado[key] = int(value)

keys = keyInOrder(puntajeProductoOrdenado, 10)

"""## Top 10 Usuarios con Mayor % en Reviews Positivos"""

c = 1
print("Top 10 Usuarios con Mayor % en Reviews Positivos")
for key, value in keys.items():
  print ("%d: %s: Con %s porcentajes de reviews positivos" % (c, key, value))
  c += 1

"""##### Usuarios con mayor y menor puntaje de positivos o negativos"""

userPorcentajeDeReviewNeg = userDicitionaryAddPoints(userPorcentajeDeReviewNeg, usersDictionaryConNegativos, userPorcentajeDeReview)
puntajeProductoOrdenado = {}
for key, value in sorted(userPorcentajeDeReview.items(), key=operator.itemgetter(1), reverse=True):
  puntajeProductoOrdenado[key] = int(value)
keys = keyInOrder(puntajeProductoOrdenado, 10)

"""## Top 10 Usuarios con Mayor % en Reviews Negativos"""

c = 1
print("Top 10 Usuarios con Mayor % en Reviews Negativos")
for key, value in keys.items():
  print ("%d: %s: Con %s porcentajes de reviews Negativos" % (c, key, value))
  c += 1

"""#### Productos de mejor calidad (mejor rating)"""

datasetProductoRating = dataset[['name','reviews.rating']]
datasetProductoRating5 = datasetProductoRating.loc[datasetProductoRating['reviews.rating'] == 5]
datasetProductoRating4 = datasetProductoRating.loc[datasetProductoRating['reviews.rating'] == 4]


dictionaryPoints = {}

# def addPointsToDictionary(dictionaryOfPoints, columnName, givenDataset, pointsGiven):
dictionaryPoints = addPointsToDictionary(dictionaryPoints, 'name', datasetProductoRating5, 2)
dictionaryPoints = addPointsToDictionary(dictionaryPoints, 'name', datasetProductoRating4, 1)

puntajeProductoOrdenado = {}

for key, value in sorted(dictionaryPoints.items(), key=operator.itemgetter(1), reverse=True):
  puntajeProductoOrdenado[key] = int(value)

keys = keyInOrder(puntajeProductoOrdenado, 10)

"""## Top 10 Productos de Mejor Calidad Segun los Ratings"""

c = 1
print("Top 10 Productos de Mejor Calidad Segun los Ratings")
for key, value in keys.items():
  print ("%d: %s" % (c, key))
  c += 1

"""#### Peor calidad"""

datasetProductoRating = dataset[['name','reviews.rating']]
datasetProductoRating2 = datasetProductoRating.loc[datasetProductoRating['reviews.rating'] == 2]
datasetProductoRating1 = datasetProductoRating.loc[datasetProductoRating['reviews.rating'] == 1]


dictionaryPoints = {}

# def addPointsToDictionary(dictionaryOfPoints, columnName, givenDataset, pointsGiven):
dictionaryPoints = addPointsToDictionary(dictionaryPoints, 'name', datasetProductoRating2, 1)
dictionaryPoints = addPointsToDictionary(dictionaryPoints, 'name', datasetProductoRating1, 2)

puntajeProductoOrdenado = {}

for key, value in sorted(dictionaryPoints.items(), key=operator.itemgetter(1), reverse=True):
  puntajeProductoOrdenado[key] = int(value)

keys = keyInOrder(puntajeProductoOrdenado, 10)

"""## Top 10 Productos de Peor Calidad Segun los Ratings"""

c = 1
print("Top 10 Productos de Peor Calidad Segun los Ratings")
for key, value in keys.items():
  print ("%d: %s" % (c, key))
  c += 1

"""# Para Mejorar a los prodcutos de mala calidad"""

Rubbermaid174 = dataset[['reviews.rating', 'reviewtext']].loc[dataset['name'] == 'Rubbermaid174 Reveal Spray Mop']
Rubbermaid174BadReviews = Rubbermaid174.loc[Rubbermaid174['reviews.rating'] < 3]
Rubbermaid174BadReviews

Tide_Original  = dataset[['reviews.rating', 'reviewtext']].loc[dataset['name'] == 'Tide Original Liquid Laundry Detergent - 100 Oz']
Tide_Original = Tide_Original.loc[Tide_Original['reviews.rating'] < 3]
Tide_Original

"""Segun lo que las personas estan diciendo conforme a los 10 productos con peor calidad <br>
**Rubbermaid174:**
 * Se rompre facil
 * Mucho defecto, no funciona despues de un poco tiempo
 * Algunos dicen que no limpia <br>
 
**Tide Original:**
 * Se manacha la ropa
 * Algunos tienen problema en entender como se usa

En estos casos, el **Rubbermaid** hay que hacerle prueba antes de darlo a los clientes. tambien se puede encontrar una forma de dar garantia si se romple en el primer mes. <br><br>
**Tide Original** puede habeer una explicacion como se utiliza y buscar que tipo de ropa puede manchar <br>
"""