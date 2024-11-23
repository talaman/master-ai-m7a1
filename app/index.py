from flask import Flask, request, render_template, session, redirect
from pymongo import MongoClient
import os

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

            return render_template("home.html", login = usuario, pelis = x)
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
