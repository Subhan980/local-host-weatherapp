from flask import Flask, render_template, request
import requests
from flask_mysqldb import MySQL

app = Flask(__name__)
API_KEY = "1ef925623ec4ed663bc3300f168fbb1a"


app.config['MYSQL_HOST'] = '127.0.0.1'      
app.config['MYSQL_USER'] = 'root'           
app.config['MYSQL_PASSWORD'] = ''          
app.config['MYSQL_DB'] = 'App_db'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)


def save_city(city, temp, desc, humidity):
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO favorites (city, temp, `desc`, humidity)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                temp = VALUES(temp),
                `desc` = VALUES(`desc`),
                humidity = VALUES(humidity)
        """, (city, temp, desc, humidity))
        mysql.connection.commit()
        cur.close()
    except Exception as e:
        print("Error saving city:", e)



def get_saved_cities():
    cur = mysql.connection.cursor()
    cur.execute("SELECT city, temp, `desc`, humidity FROM favorites ORDER BY id DESC")
    cities = cur.fetchall()
    cur.close()
    return cities


@app.route("/", methods=["GET", "POST"])
def index():
    weather = None
    city = request.form.get("city")

    if city:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        res = requests.get(url).json()

        if res.get("cod") == 200:
            weather = {
                "city": res["name"],
                "temp": res["main"]["temp"],
                "desc": res["weather"][0]["description"].title(),
                "humidity": res["main"]["humidity"]
            }
            save_city(weather["city"], weather["temp"], weather["desc"], weather["humidity"])
        else:
            weather = {"error": "City not found!"}

    favorites = get_saved_cities()
    return render_template("weatherapp.html", weather=weather, favorites=favorites)


if __name__ == "__main__":
    app.run(debug=True, port=5014)
