import os
from flask import Flask , render_template, request, render_template_string, redirect, url_for
from pymongo import MongoClient

db = MongoClient(os.getenv("MONGO_URL"))["Sign-in"]
collection = db["Students"]

app = Flask(__name__, static_folder="styles")
app.secret_key = str(os.getenv("FLASK_SECRETE_KEY"))

@app.route("/")
def sign_in():
    return render_template("index.html")

# @app.route("/auth", methods=["POST"])
# def auth():
#     rollNo = request.form.get('rollNo')
#     DOB = request.form.get('DOB')
#     validation = collection.find_one({"rollNo": int(51466), "DOB": str("26-03-2019")})
#     # validation = collection.find_one({'rollNo': str(username), 'DOB': str(password)})
#     if validation:
#         return render_template_string("""
#             <!DOCTYPE html>
#             <html>
#             <body>
#                 YES
#             </body>
#             </html>
#                 """)
#     else:
#         return redirect(url_for("sign_in"))
    
# @app.route("")


@app.route("/auth", methods=["POST"])
def auth():
    roll_no = request.form.get('rollNo', '').strip()  # Remove extra spaces
    dob = request.form.get('DOB', '').strip()  # Remove spaces

    # Convert roll number to integer (if stored as int in DB)
    try:
        roll_no = int(roll_no)
    except ValueError:
        return redirect(url_for("sign_in"))  # Invalid roll number input

    # Check if the user exists
    validation = collection.find_one({"rollNo": roll_no, "DOB": dob})

    if validation:
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







if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
