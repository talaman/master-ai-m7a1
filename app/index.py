from flask import Flask, request, render_template, session, redirect
from pymongo import MongoClient
import os
import math
import statistics

app = Flask(__name__)

connectionString = os.getenv("MONGO_CONNECTIONSTRING")


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
