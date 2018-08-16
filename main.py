from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def upload_form():
    if request.method == 'GET':
        return render_template('form.html')
    else:
        return redirect(url_for('map'))

@app.route('/map', methods=['GET'])
def map():
    return render_template('map.html')