from flask import Flask, request, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
from bson import ObjectId
import os

load_dotenv()

app = Flask(__name__)

# MongoDB configuration
MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("MONGODB_DATABASE")

# Connect to MongoDB Atlas
client = MongoClient(
    MONGODB_URI,
    serverSelectionTimeoutMS=10000
)

db = client[DATABASE_NAME]

students = db["students"]


@app.route("/")
def home():

    try:
        client.admin.command("ping")

        return jsonify({
            "message": "Student Record API is running",
            "mongodb": "Connected"
        })

    except Exception as e:

        print("MongoDB CONNECTION ERROR:", repr(e))

        return jsonify({
            "message": "Student Record API is running",
            "mongodb": "Connection failed",
            "error": str(e)
        }), 500


# CREATE
@app.route("/students", methods=["POST"])
def create_student():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    result = students.insert_one(data)

    return jsonify({
        "message": "Student created successfully",
        "id": str(result.inserted_id)
    }), 201


# READ ALL
@app.route("/students", methods=["GET"])
def get_students():

    student_list = []

    for student in students.find():

        student["_id"] = str(student["_id"])

        student_list.append(student)

    return jsonify(student_list)


# READ ONE
@app.route("/students/<student_id>", methods=["GET"])
def get_student(student_id):

    try:

        student = students.find_one({
            "_id": ObjectId(student_id)
        })

        if not student:

            return jsonify({
                "error": "Student not found"
            }), 404

        student["_id"] = str(student["_id"])

        return jsonify(student)

    except Exception:

        return jsonify({
            "error": "Invalid student ID"
        }), 400


# UPDATE
@app.route("/students/<student_id>", methods=["PUT"])
def update_student(student_id):

    data = request.get_json()

    if not data:

        return jsonify({
            "error": "Request body is required"
        }), 400

    try:

        result = students.update_one(
            {
                "_id": ObjectId(student_id)
            },
            {
                "$set": data
            }
        )

        if result.matched_count == 0:

            return jsonify({
                "error": "Student not found"
            }), 404

        return jsonify({
            "message": "Student updated successfully"
        })

    except Exception:

        return jsonify({
            "error": "Invalid student ID"
        }), 400


# DELETE
@app.route("/students/<student_id>", methods=["DELETE"])
def delete_student(student_id):

    try:

        result = students.delete_one({
            "_id": ObjectId(student_id)
        })

        if result.deleted_count == 0:

            return jsonify({
                "error": "Student not found"
            }), 404

        return jsonify({
            "message": "Student deleted successfully"
        })

    except Exception:

        return jsonify({
            "error": "Invalid student ID"
        }), 400


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
