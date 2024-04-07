
#Flask web application with routes for index, map, and location.
#index() renders index.html template.
#map() renders map.html template. 
#location() handles POST request to /location, gets lat/lng from form, 
#prints to console, and renders location_saved.html template.
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/map')
def map():
    return render_template('map.html')

@app.route('/location', methods=['POST'])
def location():
    lat = request.form['lat']
    lng = request.form['lng']
    
    print(f"Latitude: {lat}, Longitude: {lng}")
    return render_template('location_saved.html', lat=lat, lng=lng)

if __name__ == '__main__':
    app.run(debug=True)
