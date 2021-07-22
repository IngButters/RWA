from flask import Flask, render_template, request
import os
import pandas as pd
import matplotlib.pyplot as plt
from flask_sqlalchemy import SQLAlchemy
import sqlite3

currentdirectory = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)



@app.route("/")
@app.route("/home")
def home_page():
    return render_template('home.html')# this redirects to my html file

@app.route('/tetis', methods = ['GET','POST'])
def tetis_page():

    return render_template('tetis.html')


@app.route("/climatologia")
def climatologia_page():
    #Connect the database
    connection = sqlite3.connect(currentdirectory + "\clima.db")
    cursor = connection.cursor()

    return render_template('climatologia.html')# this redirects to my html file

if __name__ == '__main__': #checks if our file executes directly and not imported
    app.run(debug=True) #



