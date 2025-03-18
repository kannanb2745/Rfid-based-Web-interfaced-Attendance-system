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


Attendance = client["Students"]["Attendance"]
StudentAttendance = client["Students"]
# MetaData Databases
meta_db = client["MetaData"]
MetaDataStudents = meta_db["Students"]
MetaDataEntries = meta_db["Entries"]

admin_db = client["AdminDataBase"]
AdminStudentList = admin_db["StudentsList"] # -> Students list of there data 
# AdminAttendance = admin_db["Attendance"]  # Entries of there grouped by date

#TODO:Need to write the common Logout function for admin and student
#TODO: need to write query for admin and some other patch work like fetching details in mongodb

app = Flask(__name__, static_folder="styles")
app.secret_key = str(os.getenv("FLASK_SECRETE_KEY"))

@app.route("/")
def sign_in():
    return render_template("index.html")

# from flask import session, redirect, url_for
# 
# Store data in session instead of passing in URL
# session["_rfidTag"] = student_data.get("rfidTag")
# session["_name"] = student_data.get("name")
# session["_rollNo"] = rollNumber
# session["_department"] = student_data.get("department")
# 
# return redirect(url_for("student_dashboard"))
# 
# from flask import session

# @app.route('/student-dashboard')
# def student_dashboard():
#     rfidTag = session.get("_rfidTag")
#     name = session.get("_name")
#     rollNo = session.get("_rollNo")
#     department = session.get("_department")

#     return render_template("student_dashboard.html", rfidTag=rfidTag, name=name, rollNo=rollNo, department=department)




@app.route("/auth", methods=["POST"])
def auth():
    rollNumber = request.form.get('rollNo', '').strip()  # Remove extra spaces
    dob = request.form.get('DOB', '').strip()  # Remove spaces
    try:
        if rollNumber == "admin":
            validation = collection.find_one({"rollNo": rollNumber, "DOB": dob})
            if validation:
                return redirect(url_for("admin_dashboard"))
            else:
                return redirect(url_for("sign_in"))
        else:
            validation = collection.find_one({"rollNo": rollNumber, "DOB": dob})
            if validation:
                student_data = dict(MetaDataStudents.find_one({'rollNumber': str(rollNumber)}))
                return redirect(url_for("student_dashboard", _rfidTag=student_data.get("rfidTag"), _name=student_data.get("name"), _rollNo=rollNumber, _department=student_data.get("department")))  
            else:
                return redirect(url_for("sign_up"))
    except ValueError:
        return redirect(url_for("sign_in"))  # Invalid roll number input

@app.route("/logout", methods=["POST"])
def logout():
    print(request.json)
    return redirect(url_for("sign_in"))
@app.route('/admin-dashboard')
def admin_dashboard():
    return render_template("admin_dashboard.html")



#TODO: May be change this url to admin-generate-attendance
@app.route("/api/generate-attendance", methods=["POST"])
def generate_attendance():
    data = request.json  # Receive JSON input
    print("Received JSON:", data)  # Debugging output

    if not data:
        return jsonify({"error": "No data received"}), 400

    day = data.get("day")
    month = data.get("month")
    year = data.get("year")
    month = str(month).zfill(2)
    day = str(day).zfill(2)
    print(day, month, year)

    if not day or not month or not year:
        return jsonify({"error": "Invalid date input"}), 400

    # Simulating empty attendance for certain cases
    if int(day) > 31 or int(month) > 12 or int(year) < 2000:
        return jsonify([])  # Return an empty list if invalid data is passed

    
    # students_collection = StudentAttendance[f"Attendance.{rfidTag}"]
    AdminAttendance = admin_db[f"Attendance.{year}_{month}_{day}"]
    print(f"Attendance.{year}_{month}_{day}")    # collected_data = list(students_collection.find({'month': int(month), 'year': int(year)}))
    collected_data = AdminAttendance.find({})
    attendance_data = []
    for i in collected_data:
        student_data = dict(MetaDataStudents.find_one({'rfidTag': i["rfidTag"]}))
        name = student_data.get("name")
        rollNumber = student_data.get('rollNumber')
        attendance_data.append({
            "rollNo": rollNumber,
            "name": name,
            "date": f"{i['day']}-{i['month']}-{i['year']}",
            "entryTime": i['inTime'],
            "exitTime": i['outTime']
        })
    print("Sending Response:", attendance_data)  # Debugging output
    return jsonify(attendance_data)

@app.route("/student-dashboard")
def student_dashboard():
    # return render_template("student_dashboard.html")
    rfid_tag = request.args.get('_rfidTag')  
    name = request.args.get('_name')  
    roll_no = request.args.get('_rollNo')  
    department = request.args.get('_department')  

    return render_template("student_dashboard.html", rfidTag=rfid_tag, name=name, rollNo=roll_no, department=department)


@app.route("/api/student-generate-attendance", methods=["POST"])
def student_generate_attendance():
    data = request.json  # Receive JSON input
    
    print("Received JSON:", data)  # Debugging output
    
    if not data:
        return jsonify({"error": "No data received"}), 400
    month = data.get("month")
    year = data.get("year")
    rfidTag = data.get("rfidTag")    
    
    if not month or not year:
        return jsonify({"error": "Invalid date input"}), 400
    #TODO: where you need to check while pushing the entry if the months and year is already present or not 
    #TODO: need to create an db under Students and using rfid where for each students it contains the entry months and dates
    student_data = client["Students"][f"Attendance.{str(rfidTag)}.MetaData"]
    check = student_data.find_one({'month':str(month), 'year':str(year)})
    print(check)
    if check == None:
    # if (str(month) != str("3") or str(month) != str("4 ")) and str(year) != "2025" :
        return jsonify({"error": "No Attendance are Available"}), 400
    
    if int(month) > 12 or int(year) < 2000:
        return jsonify([])  # Return an empty list if invalid data is passed
    
    students_collection = StudentAttendance[f"Attendance.{rfidTag}"]
    collected_data = list(students_collection.find({'month': int(month), 'year': int(year)}))
    student_data = dict(MetaDataStudents.find_one({'rfidTag': rfidTag}))
    name = student_data.get("name")
    rollNumber = student_data.get('rollNumber')
    
    attendance_data = []
    for i in collected_data:
        attendance_data.append({
            "rollNo": rollNumber,
            "name": name,
            "date": f"{i['day']}-{i['month']}-{i['year']}",
            "entryTime": i['inTime'],
            "exitTime": str(i['outTime'])
        })
    
    print("Sending Response:", attendance_data)  # Debugging output
    return jsonify(attendance_data)



@app.route('/register-user', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        #NOTE: if it is in the post method the data will be stored in the db and return true to the register.js
        #NOTE: the register js will render the page again 
        try:
            data = request.get_json()

            print(data)
            student_details = {
                "name" : data.get("name"),
                "DOB" : data.get("dob"),
                "gender" : data.get("gender"),
                "email" : data.get("email"),
                "rollNumber" : str(data.get("rollNumber")),
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
    
    current_time = datetime.now()
    day = current_time.day
    month = current_time.month
    year = current_time.year
    time_str = current_time.strftime("%I:%M:%S")
    
    check = MetaDataEntries.find_one({"rfidTag": rfid_id}) 
    date_str = datetime.now().strftime("%Y_%m_%d")
    AdminAttendance = admin_db["Attendance"]
    student_entry = AdminAttendance[date_str]
    
    #TODO: need to create an db under Students and using rfid where for each students it contains the entry months and dates
    #TODO: where you need to check while pushing the entry if the months and year is already present or not 

    if check and check.get("entryStatus"):  # Check if entry exists and entryStatus is True
        # details = {
        #     "rfidTag": rfid_id,
        #     "day": day,
        #     "month": month, 
        #     "year": year,
        #     "inTime": time_str,
        #     "entry": False
        # }
        # student_entry.insert_one(details)
        
        student_entry.update_one(
            {"rfidTag": rfid_id, "outTime": "Present"},
            {"$set": {"outTime": time_str}}
                                       )
        # Attendance[rfid_id].insert_one(details)
        # check Attendance
        Attendance[rfid_id].update_one(
            {"rfidTag": rfid_id, "outTime": "Present"},
            {"$set": {"outTime": time_str}}
                                       )
        MetaDataEntries.update_one(
        {"rfidTag": rfid_id, "entryStatus": True},  # Find the document where entryStatus is True
        {"$set": {"entryStatus": False}}  # Update entryStatus to False
        )
        
        #NOTE: Card Numbers
        # {"rfidTag": 0xb331529b, "entryStatus": True}
        # 0x5297ca1b
    else:
        student_data = client["Students"][f"Attendance.{rfid_id}"]
        check = student_data["MetaData"].find_one({'month':str(month), 'year':str(year)})
        if check != True:
            student_data["MetaData"].insert_one({
                "month":str(month),
                "year":str(year)
            })
        details = {
            "rfidTag": rfid_id,
            "day": day,
            "month": month, 
            "year": year,
            "inTime": time_str,  
            "outTime": "Present", 
            "entry": True
        }
        student_entry.insert_one(details)
        Attendance[rfid_id].insert_one(details)
        MetaDataEntries.update_one(
        {"rfidTag": rfid_id, "entryStatus": False},  # Find the document where entryStatus is True
        {"$set": {"entryStatus": True}})  # Update entryStatus to False



    print(f"🟢 API Call from ESP32 - RFID ID: {rfid_id}")
    return jsonify({"message": "RFID received", "rfid": rfid_id})





if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
