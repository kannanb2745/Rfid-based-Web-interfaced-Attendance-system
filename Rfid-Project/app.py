import os
from flask import Flask , render_template, request, render_template_string, redirect, url_for, jsonify
from pymongo import MongoClient
from datetime import datetime
from time import sleep


# single MongoClient instance
client = MongoClient(os.getenv("MONGO_URL"))

# Main Database (Sign-in)
db = client["Sign-in"]
collection = db["Students"]


Attandence = client["Students"]["Attandence"]
# MetaData Databases
meta_db = client["MetaData"]
MetaDataStudents = meta_db["Students"]
MetaDataEntries = meta_db["Entries"]

admin_db = client["AdminDataBase"]
AdminStudentList = admin_db["StudentsList"] # -> Students list of there data 
AdminAttendance = admin_db["Attendance"]  # Entries of there grouped by date

#TODO: create an dynamic folder creation by date by refering the below
    # Generate collection name dynamically (Example: Attendance_YYYYMMDD or Attendance_StudentID)
    # date_str = datetime.now().strftime("%Y%m%d")  # Format: YYYYMMDD
    # collection_name = f"Attendance_{date_str}"  # Stores attendance per day
# 
    # Access or create the collection dynamically
    # attendance_collection = admin_db[collection_name]

#TODO: Just need to Write Query for getting the generating attandence



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
            roll_no = str(roll_no)
    except ValueError:
        return redirect(url_for("sign_in"))  # Invalid roll number input

    # Check if the user exists
    validation = collection.find_one({"rollNo": roll_no, "DOB": dob})

    if validation:
        if roll_no == "admin" and dob == "Admin@123":
            return redirect(url_for("admin_dashboard"))
        else:
    #TODO: Here get the data from the MetaData Database and send it to render it dynamically
            return redirect(url_for("student_dashboard"))    
    else:
        return redirect(url_for("sign_in"))




#TODO:Make the nav bard fields with proper data
@app.route('/admin-dashboard')
def admin_dashboard():
    return render_template("admin_dashboard.html")



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

@app.route("/student-dashboard")
#TODO:Change the values dynamically
def student_dashboard():
    return render_template("student_dashboard.html")

@app.route("/api/student-generate-attendance", methods=["POST"])
def student_generate_attendance():
    data = request.json  # Receive JSON input
    print("Received JSON:", data)  # Debugging output
    
    if not data:
        return jsonify({"error": "No data received"}), 400
    
    month = data.get("month")
    year = data.get("year")
    print(month, year)
    
    if not month or not year:
        return jsonify({"error": "Invalid date input"}), 400
    
    # Simulating empty attendance for certain cases
    if int(month) > 12 or int(year) < 2000:
        return jsonify([])  # Return an empty list if invalid data is passed
    
    # Generate random attendance data
    # TODO: Write a MongoDB fetch query for attendance
    attendance_data = [
        {
            "rollNo": "12063",
            "name": "John Doe",
            "date": f"{1}/{month}/{year}",
            "entryTime": "09:00 AM",
            "exitTime": "05:00 PM"
        },
        {
            "rollNo": "12064",
            "name": "Jane Smith",
            "date": f"{1}/{month}/{year}",
            "entryTime": "09:15 AM",
            "exitTime": "05:30 PM"
        }
    ]
    
    print("Sending Response:", attendance_data)  # Debugging output
    return jsonify(attendance_data)



@app.route('/register-user', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        #NOTE: if it is in the post method the data will be stored in the db and return true to the register.js
        #NOTE: the register js will render the page again 
        try:
            data = request.get_json()

            #TODO: Call the rfid functoin to get rfid tag
            print(data)
            student_details = {
                "name" : data.get("name"),
                "DOB" : data.get("dob"),
                "gender" : data.get("gender"),
                "email" : data.get("email"),
                "rollNumber" : int(data.get("rollNumber")),
                "department" : data.get("department"),
                "batchYear" : data.get("batchYear"),
                "rfidTag" : data.get("rfidTag"),
            }
            MetaDataStudents.insert_one(student_details)
            collection.insert_one({"rollNo": data.get("rollNumber"), "DOB": data.get("dob")})
            AdminStudentList.insert_one(student_details)
            MetaDataEntries.insert_one({"rfidTag" : data.get("rfidTag"), "entryStatus" : False})
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    #NOTE: Here the web render register page if no values are there like get method 
    return render_template('register_user.html',admin_dashboard='/admin-dashboard')


#NOTE: This is handling the in/out time 
@app.route('/receive-rfid', methods=['POST'])
def receive_rfid():
    """Receive RFID data from ESP32"""
    data = request.json
    rfid_id = data.get("rfid")

    # Store RFID in MongoDBcheck = MetaDataEntries.find_one({"rfidTag": rfid_id})  # Corrected query syntax
    current_time = datetime.now()
    day = current_time.day
    month = current_time.month
    year = current_time.year
    time_str = current_time.strftime("%I:%M:%S %p")
    
    check = MetaDataEntries.find_one({"rfidTag": rfid_id}) 
    date_str = datetime.now().strftime("%Y_%m_%d")
    student_entry = AdminAttendance[date_str]
    
    if check and check.get("entryStatus"):  # Check if entry exists and entryStatus is True
        details = {
            "rfidTag": rfid_id,
            "day": day,
            "month": month, 
            "year": year,
            "time": time_str,  
            "entry": False
        }
        student_entry.insert_one(details)
        Attandence[rfid_id].insert_one(details)
        MetaDataEntries.update_one(
        {"rfidTag": rfid_id, "entryStatus": True},  # Find the document where entryStatus is True
        {"$set": {"entryStatus": False}}  # Update entryStatus to False
        )
        
        #NOTE: Card Numbers
        # {"rfidTag": 0xb331529b, "entryStatus": True}
        # 0x5297ca1b
    else:
        details = {
            "rfidTag": rfid_id,
            "day": day,
            "month": month, 
            "year": year,
            "time": time_str,  
            "entry": True
        }
        student_entry.insert_one(details)
        Attandence[rfid_id].insert_one(details)
        MetaDataEntries.update_one(
        {"rfidTag": rfid_id, "entryStatus": False},  # Find the document where entryStatus is True
        {"$set": {"entryStatus": True}})  # Update entryStatus to False



    print(f"🟢 API Call from ESP32 - RFID ID: {rfid_id}")
    return jsonify({"message": "RFID received", "rfid": rfid_id})





if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
