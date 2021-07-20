from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
@app.route("/Inicio")
def home_page():
    return render_template('home.html')# this redirects to my html file

@app.route('/Tetis')
def tetis_page():
    return render_template('tetis.html')

