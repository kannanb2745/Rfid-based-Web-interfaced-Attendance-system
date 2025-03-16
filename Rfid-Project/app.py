import os
from flask import Flask , render_template, request, render_template_string, redirect, url_for, jsonify
from pymongo import MongoClient

db = MongoClient(os.getenv("MONGO_URL"))["Sign-in"]
collection = db["Students"]

app = Flask(__name__, static_folder="styles")
app.secret_key = str(os.getenv("FLASK_SECRETE_KEY"))

@app.route("/")
def sign_in():
    return render_template("index.html")

@app.route("/auth", methods=["POST"])
def auth():
    roll_no = request.form.get('rollNo', '').strip()  # Remove extra spaces
    dob = request.form.get('DOB', '').strip()  # Remove spaces

    # Convert roll number to integer (if stored as int in DB)
    try:
        if roll_no != "admin":
            roll_no = int(roll_no)
    except ValueError:
        return redirect(url_for("sign_in"))  # Invalid roll number input

    # Check if the user exists
    validation = collection.find_one({"rollNo": roll_no, "DOB": dob})

    if validation:
        if roll_no == "admin" and dob == "Admin@123":
            return redirect(url_for("admin_dashboard"))
        else:
            return render_template_string("""
                <!DOCTYPE html>
                <html>
                <body>
                    <h1>YES</h1>
                </body>
                </html>
            """)
    else:
        return redirect(url_for("sign_in"))




#TODO:Make the nav bard fields with proper data
@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template("admin_dashboard.html", _id=str(123465), _dept=str("Computer Scince"))



#TODO:Store the data in the mongo db and in sign-in page 
#NOTE:CHANGE THE DATE IN this format in sign-in page placeholder -> year-month-date
@app.route('/register-user', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        #NOTE: if it is in the post method the data will be stored in the db and return true to the register.js
        #NOTE: the register js will render the page again 
        try:
            data = request.get_json()
            #TODO:Here need to push these values into Mongodb under -> {Metadata, Students_list, rfid & DOB -> Sign-in,  }
            # Here you would typically save to a database using db.session.add and db.session.commit
            print(data)
            print(rfid_entry())
            print(data.get("name"), data.get("dob"), data.get("gender"), data.get("email"), data.get("rollNumber"), data.get("department"), data.get("batchYear"))
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    #NOTE: Here the web render register page if no values are there like get method 
    return render_template('register_user.html',admin_dashboard='/admin_dashboard', _id=str(123465), _dept=str("Computer Scince"))

def rfid_entry():
    # sleep(3)
    #TODO: Make here the MQTT call to the Esp32 and get the details 
    return str(123434)


#TODO: Wrrite an mongodb fecth data query for attadence 
@app.route("/api/generate-attendance", methods=["POST"])
def generate_attendance():
    data = request.json  # Receive JSON input
    print("Received JSON:", data)  # Debugging output

    if not data:
        return jsonify({"error": "No data received"}), 400

    day = data.get("day")
    month = data.get("month")
    year = data.get("year")
    print(day, month, year)

    if not day or not month or not year:
        return jsonify({"error": "Invalid date input"}), 400

    # Simulating empty attendance for certain cases
    if int(day) > 31 or int(month) > 12 or int(year) < 2000:
        return jsonify([])  # Return an empty list if invalid data is passed

    # Generate random attendance data
    #TODO:While Storing the in/out attandence store it on day,month,year separate field
    attendance_data = [
        {
            "rollNo": "12063",
            "name": "John Doe",
            "date": f"{day}/{month}/{year}",
            "entryTime": "09:00 AM",
            "exitTime": "05:00 PM"
        },
        {
            "rollNo": "12064",
            "name": "Jane Smith",
            "date": f"{day}/{month}/{year}",
            "entryTime": "09:15 AM",
            "exitTime": "05:30 PM"
        }
    ]

    print("Sending Response:", attendance_data)  # Debugging output
    return jsonify(attendance_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
