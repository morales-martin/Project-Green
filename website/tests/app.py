from flask import Flask, render_template, url_for
import os
import json
import urllib.request
import sqlite3
import matplotlib.pyplot as plt
import numpy as np
import pymysql
import datetime

app = Flask(__name__)

'''
borrowed code - deals with browser cache issue (does not update css file)
source = http://flask.pocoo.org/snippets/40/
works by overriding Flask's url_for function, if used on static source it
generates url with time-stamp appended to it (guarantees CSS update)
'''
@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)


@app.route('/getJson/<ip>/<kind>/<num>')
def getJson(ip, kind, num):
    '''
    getJson route

    ip - sensor server address
    kind - type of sensor
       t -> temperature
       h -> humidity
       m -> moisture
       n -> normal light
       u -> uv light
    '''

    # makes call to server and puts response into dictionary
    url = "http://" + ip
    res = urllib.request.urlopen(url)
    data_dict = json.loads(res.read().decode('utf-8'))
    
    # current date-time
    date = datetime.datetime.now().strftime("%I:%M:%s%p on %B %d, %Y")
    
    # uses kind arg to retrieve data from dictionary - creates sql insert query string
    # as well as list used to send arguments for query
    if kind == 't':
        data = data_dict["temperature"][0]
        data_f = 9.0/5.0 * data + 32
        sql = "INSERT INTO Temperature (ID, Fahrenheit, Celsius, DATE) VALUES (?, ?, ?, ?)"
        values = (num, data_f, data, date)
    elif kind == 'h':
        data = data_dict["humidity"][0]
        sql = "INSERT INTO Humidity (ID, Humidity, DATE) VALUES (?, ?, ?)"
        values = (num, data, date)
    elif kind == 'm':
        data = data_dict["moisture"][0]
        sql = "INSERT INTO Moisture (ID, Moisture, Date) VALUES (?, ?, ?)"
        values = (num, data, date)
    elif kind == 'n':
        data = data_dict["visible_light"][0]
        sql = "INSERT INTO Light (ID, Light, DATE) VALUES (?, ?, ?)"
        values = (num, data, date)
    else:
        data = data_dict["UV_light"][0]
        sql = "INSERT INTO UV (ID, UVIndex, DATE) VALUES (?, ?, ?)"
        values = (num, data, date)

    # connects to database, then returns data in order to display in flask view
    db = sqlite3.connect("/home/pi/project_green/Database/GreenhouseSensors")
    c = db.cursor()
    c.execute(sql, values)
    db.commit()
    c.close()
    db.close()
    
    return str(data)

# intro page
@app.route('/')
def index():
    return render_template('index.html')

# demo start page
@app.route('/demo')
def demo():
    return render_template('demo_start.html')

'''
    moisture sensor page
    recieves id and ip address as parameters, which are sent to html template
'''
@app.route('/demo/moisture/<num>/<address>')
def moisture(num, address):
    return render_template('moisture.html', ip = address, num = num)

'''
    temp/humi page
    recieves id and ip address as parameters, which are sent to html template
''' 
@app.route('/demo/temp-humi/<address>/<num>')
def th_sensor(address, num):
    return render_template('th_sensor.html', ip = address, num = num)

'''
    light page
    recieves id and ip address as parameters, which are sent to html template
''' 
@app.route('/demo/light/<address>/<num>')
def light(num, address):
    return render_template('light_sensor.html', ip = address, num = num)

def populate_ids(ids, start, end):
    num = start
    range_end = end - start + 1
    for ndx in range(0, range_end):
        np.append(ids, num)
        print(num)
        num += 1

@app.route('/make_graph/<which>/<start>/<end>')
def make_graph(which, start, end):
    '''
       make_graph route
         not rendered as full page, but used with AJAX in order to update page
         dynamically
    '''

    # uses which in order to create custom select sql query, as well as plot labels
    if which == 't':
        name = "Temperature Data"
        ylabel = "Temperature"
        sql = "SELECT Celsius FROM Temperature WHERE rowid BETWEEN " + start + " AND " + end
    elif which == 'h':
        name = "Humidity Data"
        ylabel = "Humidity"
        sql = "SELECT Humidity FROM Humidity WHERE rowid BETWEEN " + start + " AND " + end 
    elif which == 'm':
        name = "Moisture Data"
        ylabel = "Moisture"
        sql = "SELECT Moisture FROM Moisture WHERE rowid BETWEEN " + start + " AND " + end
    elif which == 'n':
        name = "Light Intensity Data"
        ylabel = "Light Intensity"
        sql = "SELECT Light FROM Light WHERE rowid BETWEEN " + start + " AND " + end
    else:
        name = "UV Index"
        ylabel = "UV Index"
        sql = "SELECT UVIndex FROM UV WHERE rowid BETWEEN " + start + " AND " + end

    # connects to database and retrieves data (put in rows)
    db = sqlite3.connect("/home/pi/project_green/Database/GreenhouseSensors")
    c = db.cursor()
    
    c.execute(sql)
    rows = c.fetchall()
    
    c.close()
    db.close()
    
    # uses numpy to create plot data arrays (start and end parameters tell range of ids)
    # data is created derictly from rows
    ids = np.arange(int(start), int(end) + 1)
    data = np.array(rows)

    
    # creates plot
    fig, ax = plt.subplots()
    ax.xaxis.set_ticks(np.arange(min(ids), max(ids) + 1, 1.0))
    ax.plot(ids, data)

    ax.set(xlabel='ID', ylabel=ylabel, title=name)
    ax.grid()

    url = "images/graphs/graph.png"
    fig.savefig("static/" + url)

    return render_template('graph.html', url = url)

@app.route('/make_table/<which>/<start>/<end>')
def make_table(which, start, end):
	'''
	    make_graph route
		 not rendered as full page, but used with AJAX in order to update page
		 dynamically
	'''

	# uses which in order to create custom select sql query, as well as plot labels
	if which == 't':
		name = "Temperature Data"
		ylabel = "Temperature"
		sql = "SELECT Celsius FROM Temperature WHERE rowid BETWEEN " + start + " AND " + end
	elif which == 'h':
		name = "Humidity Data"
		ylabel = "Humidity"
		sql = "SELECT Humidity FROM Humidity WHERE rowid BETWEEN " + start + " AND " + end 
	elif which == 'm':
		name = "Moisture Data"
		ylabel = "Moisture"
		sql = "SELECT Moisture FROM Moisture WHERE rowid BETWEEN " + start + " AND " + end
	elif which == 'n':
		name = "Light Intensity Data"
		ylabel = "Light Intensity"
		sql = "SELECT Light FROM Light WHERE rowid BETWEEN " + start + " AND " + end
	else:
		name = "UV Index"
		ylabel = "UV Index"
		sql = "SELECT UVIndex FROM UV WHERE rowid BETWEEN " + start + " AND " + end

	# connects to database and retrieves data (put in rows)
	db = sqlite3.connect("/home/pi/project_green/Database/GreenhouseSensors")
	c = db.cursor()
	
	c.execute(sql)
	rows = c.fetchall()

	c.close()
	db.close()

	# data is created derictly from rows
	data = np.array(rows)

	# compact rows together for table
	for row in data:
		cell_Text.append(row)

	# creates table
	table = plt.table(cellText = cell_Text,colLabels = ('Range', 'Measurement'),loc='center')

	plt.axis('off')
	plt.grid('off')
	
	url = "images/tables/table.png"
	fig.savefig("static/" + url)
	
	return render_template('table.html', url = url)
	

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
