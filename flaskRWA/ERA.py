from flask import Flask, render_template, request
import os
import pandas as pd
import matplotlib.pyplot as plt
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)

filename = 'C:/Users/Bender/Desktop/Mapas_ERA/RWA/RWA/flaskRWA/static/precipitacion_sup.csv'
df_precip_sup = pd.read_csv(filename)




@app.route("/")
@app.route("/home")
def home_page():
    return render_template('home.html')# this redirects to my html file

@app.route('/tetis', methods = ['GET','POST'])
def tetis_page():

    return render_template('tetis.html')

if __name__ == '__main__': #checks if our file executes directly and not imported
    app.run(debug=True) #




"""     if request.method == 'POST':
        file = request.files['csvfile']
        if not os.path.isdir('static'):
            os.mkdir('static')
        filepath = os.path.join('static', file.filename)
        file.save(filepath)
      
        return render_template('tetis.html')
        #'El nombre del archivo seleccionado es: {}'.format(file.filename) """