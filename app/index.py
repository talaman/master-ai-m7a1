from flask import Flask, request, render_template, session, redirect
from pymongo import MongoClient
import os
import math
import statistics
import pandas as pd

app = Flask(__name__)

connectionString = os.getenv("MONGO_CONNECTIONSTRING")

@app.route("/informe",methods=['GET'])
def informe():
    pelis = carga_peliculas()
    listed_in = get_listed_in(pelis)
    listed_in_count = get_listed_in_count(pelis)
    countries_count = get_countries_count(pelis)
    valoraciones = get_valoraciones()
    media_valoracion = get_valoracion_media(valoraciones)
    suma_valoracion = get_valoracion_suma(valoraciones)
    valoracion_media_peliculas = get_valoracion_media_peliculas(valoraciones)
    
    
    return render_template("informe.html", 
    pelis = pelis, 
    listed_in_count = listed_in_count,
    countries_count = countries_count,
    valoraciones = valoraciones,
    media_valoracion = media_valoracion,
    suma_valoracion = suma_valoracion,
    valoracion_media_peliculas = valoracion_media_peliculas)

def carga_peliculas():
    # carga dataframe de peliculas en data/netflix_titles.csv, la primera fila es el header
    df = pd.read_csv('data/netflix_titles.csv',header=0)
    return df

def get_listed_in(df):
    # obtiene la columna listed_in y la convierte en una lista de strings
    listed_in = df['listed_in'].tolist()
    # devide por comas cada string de la lista y lo convierte en una sola lista con valores unicos
    listed_in = list(set([x.strip() for sublist in [x.split(',') for x in listed_in] for x in sublist]))
    # ordena la lista por mayor cantidad de valores
    listed_in.sort(key=lambda x: len(x), reverse=True)
    return listed_in

def get_listed_in_count(df):
    # obtiene la columna listed_in y la convierte en una lista de strings
    listed_in = df['listed_in'].tolist()
    # devide por comas cada string de la lista y lo convierte en una sola lista
    listed_in = [x.strip() for sublist in [x.split(',') for x in listed_in] for x in sublist]
    # cuenta la cantidad de veces que aparece cada valor en la lista
    listed_in = pd.Series(listed_in).value_counts()
    return listed_in

def get_countries_count(df):
    # obtiene la columna country y la convierte en una lista de strings
    country = df['country'].dropna().tolist()
    # divide por comas cada string de la lista y lo convierte en una sola lista
    country = [x.strip() for sublist in [x.split(',') for x in country] for x in sublist]
    # cuenta la cantidad de veces que aparece cada valor en la lista
    country = pd.Series(country).value_counts()
    return country

def get_valoraciones():
    # hace join de las tablas peliculas y valoraciones desde mongo
    # devuelve un dataframe con las valoraciones de cada usuario por pelicula
    # debe mostrar 3 campos: usuarios.login, peliculas.nombre, valoraciones.valoraciones (dependiendo del usuario y la pelicula que es el nombre del key)
    # ejemplo: [['pantolin','pelicula1',5],['pantolin','pelicula2',4],['pantolin','pelicula3',3],['pantolin','pelicula4',2],['pantolin','pelicula5',1]]	
    client = MongoClient (connectionString)
    db = client['filmnet']
    collection = db['usuarios']
    x = collection.find({})
    usuarios = []
    for elem in x:
        usuarios.append(elem['login'])
    collection = db['valoracion']
    filmnet = list(collection.find())
    valoraciones = []
    for elem in filmnet:
        for key, value in elem['valoraciones'].items():
            valoraciones.append([elem['usuario'],key,value])
    return valoraciones

def get_valoracion_media(valoraciones):
    # calcula la media total de todas las valoraciones, devuelve un float
    return statistics.mean([x[2] for x in valoraciones])

def get_valoracion_suma(valoraciones):
    # calcula la suma total de todas las valoraciones, devuelve un int
    return sum([x[2] for x in valoraciones])
 
def get_valoracion_media_peliculas(valoraciones):
    # calcula la media de todas las valoraciones por pelicula, devuelve un diccionario con el nombre de la pelicula y la media
    z = {}
    for elem in valoraciones:
        if elem[1] in z:
            z[elem[1]].append(elem[2])
        else:
            z[elem[1]] = [elem[2]]
    for key, value in z.items():
        z[key] = statistics.mean(value)

    # orderna el diccionario por mayor valor
    z = dict(sorted(z.items(), key=lambda item: item[1], reverse=True))
    return z


    

@app.route("/",methods=['POST','GET'])
def validar():
    if request.method == 'POST':
        usuario = request.form["login"]
        password = request.form["password"]
        client = MongoClient (connectionString)
        db = client['filmnet']
        collection = db['usuarios']
        x = collection.find_one({'login':usuario, 'password':password})
        if x:
            collection = db['peliculas']
            x = collection.find({})

            #-------------------Calculo de recomendaciones-------------------
            x_p = collection.find({})

            peliculas = []
            for elem in x_p:
                peliculas.append(elem['nombre'])

            usuarios = []
            collection = db['usuarios']
            x2 = collection.find({})
            for elem in x2:
                usuarios.append(elem['login'])

            collection = db['valoracion']
            filmnet = list(collection.find())
            print('usuarios',usuarios)
            print('filmnet',filmnet)

            def devolver_valoraciones(usuario):
                for i, elem in enumerate(filmnet):
                    if elem['usuario'] == usuario:
                        return(elem['valoraciones'])

            def calcularmedia(valoracion1,valoracion2):
                cont = 0
                suma1 = 0
                suma2 = 0
                r_a = []
                r_b = []
                for elem in valoracion1:
                    if elem in valoracion2:
                        cont += 1
                        suma1 += valoracion1.get(elem)
                        suma2 += valoracion2.get(elem)
                        r_a.append(valoracion1.get(elem))
                        r_b.append(valoracion2.get(elem))
                return(r_a, r_b, suma1/cont, suma2/cont)
            #---
            def calcular_similitud(usuario1, usuario2):
                val1 = devolver_valoraciones(usuario1)
                val2 = devolver_valoraciones(usuario2)
                r_a, r_b, r_a_med, r_b_med = calcularmedia(val1,val2)
                
                numerador = 0
                denominador1 = 0
                denominador2 = 0
                
                for i, elem in enumerate(r_a):
                    numerador += (elem - r_a_med) * (r_b[i] - r_b_med)
                    denominador1 +=  ((elem - r_a_med) ** 2)
                    denominador2 +=  ((r_b[i] - r_b_med) ** 2)

                return(numerador/(math.sqrt(denominador1) * math.sqrt(denominador2)))

            def calcular_similitudes():
                matriz = {}
                for i in range(0,len(usuarios)):
                    elem = {}
                    for j in range(0,len(usuarios)):
                        if i != j:
                            elem[usuarios[j]] = calcular_similitud(usuarios[i],usuarios[j])
                    matriz[usuarios[i]] = elem
                return(matriz)


            def usuarios_parecidos(usuario, g):
                l = []
                valoracion = m[usuario]
                for key, value in valoracion.items():
                    if value >= g:
                        l.append(key)
                return l
            
            #---
            def devolver_pelicula_preferida(usuario):
                p = -1
                reco = ""
                for i in range(0,len(filmnet)):
                    if usuario == filmnet[i]['usuario']:
                        valoracion = filmnet[i].get('valoraciones')
                        for j in range(0,len(peliculas)):
                            #si no se ha valorado predecimos
                            if not peliculas[j] in valoracion:
                                aux = prediccion(usuario,peliculas[j])
                                if aux > p:                                         
                                    reco = peliculas[j]
                                    p = aux
                return(reco)

            def calcular_media_total(usu):
                val = devolver_valoraciones(usu)
                return(statistics.mean(tuple(val.values())))


            def prediccion(usu, pelicula):
                l = usuarios_parecidos(usu,0.7)
                numerador = 0
                denominador = 0
                for i in l:
                    numerador += m[usu][i] * (devolver_valoraciones(i).get(pelicula,0) - calcular_media_total(i))
                    denominador += m[usu][i]
                return(numerador / denominador + calcular_media_total(usu))

            def devolver_datos_pelicula(pelicula):
                collection = db['peliculas']
                x3 = collection.find_one({'nombre':pelicula})
                if x3:
                    return(x3)
                
            m = calcular_similitudes()
            l1 = devolver_pelicula_preferida('pantolin')
            fav = devolver_datos_pelicula(l1)
            print('m',m)
            print('l1',l1)
            print('fav',fav)
            #-----------------------------------------------------------------


            return render_template("home.html", login = usuario, pelis = x, favorita = fav)
        else:
            return render_template("login.html",error = True)

    return render_template("login.html")

@app.route("/detalle",methods=['POST','GET'])
def detalle():
    if request.method == 'POST':
        usuario = request.form["login"]
        peli = request.form["peli"]
        client = MongoClient (connectionString)
        db = client['filmnet']
        collection = db['peliculas']
        x = collection.find_one({'nombre':peli})
        #obtengo la pelicula indicada por el usuario en la BD, por si no existe
        collection2 = db['valoracion']
        x2 = collection2.find_one({'usuario':usuario})
        val = x2['valoraciones'].get(peli,0)
 
        return render_template("detalle.html", login=usuario, pelicula=x, valoracion=val)

@app.route("/actualizar_like",methods=['POST','GET'])
def actualizar_like():
    print("1")
    if request.method == 'POST':
        valor = request.form["value"]
        usuario = request.form["usuario"]
        pelicula = request.form["pelicula"]
        print(valor)

        client = MongoClient (connectionString)
        db = client['filmnet']
        collection = db['valoracion']
        x = collection.find_one({'usuario':usuario})
        valoracion_nueva = x["valoraciones"]
        print(valoracion_nueva)
        valoracion_nueva[pelicula] = int(valor)
        print(valoracion_nueva)
        collection.update_one({'usuario':usuario},{"$set":{"valoraciones":valoracion_nueva}}) 
        
        return("ok")



if __name__ == "__main__":
    app.run(port=8000,debug=True)
