from flask import Flask
from flask import redirect
from flask import url_for
from flask import render_template
from flask import request
from math import sqrt, floor
from pymongo import MongoClient
from pymongo import ReturnDocument
import requests
from random import randint

app = Flask('Daserit')
client = MongoClient('mongodb://localhost:27017/')
db = client.Daserit

@app.route('/map')
def map():
    return render_template('map.html')

def fetchHexFromDB(hex_id):
    hexes = db.hexes
    hex = hexes.find_one({"hex_id": hex_id})
    if hex == None:
        content = ''
    else:
        content = hex['content']
    return content

@app.route('/hex/<hex_id>', methods=['GET', 'POST'])
def hex(hex_id=None):
    tpl_file='hexread.html'
    hexes = db.hexes
    if request.method == 'POST':
        post_content = request.form['content']
        hex = hexes.find_one_and_update(
            {"hex_id": hex_id}, {'$set': {"content": post_content}}, 
            upsert=True,
            return_document=ReturnDocument.AFTER)
        content = hex['content']
    else:
        content = fetchHexFromDB(hex_id)
        if request.args.get('mode') == 'edit':
            tpl_file = 'hexwrite.html'
        if content == '':
            tpl_file = 'hexwrite.html'
            content = ' '.join(['#Hex:', hex_id, '#'])
    return render_template(tpl_file, id=hex_id, content=content)

@app.route('/coords')
def coords():
    def process_arg(x): return int(request.args.get(x))
    x = process_arg('x')
    y = process_arg('y')
    hex_id = fetch_hex(x,y)

    return redirect(url_for('hex', hex_id=hex_id))
    

def fetch_hex(x,y):
    radius = 40/3.0
    width = radius * 2
    height = int(radius * sqrt(3))
    side = radius * 3 / 2
    
    def set_cell_index(i,j):
        mx = i * side
        my = height * (2 * j + (i % 2)) / 2
        return {'i': i, 'j': j, 'x': mx, 'y': my}
    
    ci = floor(x/side)
    cx = x - side * ci
    
    ty = y - (ci % 2) * height / 2
    cj = floor(ty/height)
    cy = ty - height * cj
    
    if cx > abs(radius / 2 - radius * cy / height):
        hex_coords = set_cell_index(ci, cj)
    else:
        hex_coords = set_cell_index(ci - 1, cj + (ci % 2) - ((0, 1)[cy < height / 2 == True]))

    # Has to be a string because its too big for mongo
    hex_id = '1' + ''.join(['{0:0>4}'.format(int(hex_coords[x])) for x in ['i', 'j', 'x', 'y']])
    return hex_id
