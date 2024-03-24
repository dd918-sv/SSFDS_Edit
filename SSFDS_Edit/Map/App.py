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
