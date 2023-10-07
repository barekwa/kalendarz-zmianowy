from datetime import datetime

from bson import ObjectId
from flask import Flask
from flask import request, jsonify
from pymongo import MongoClient

from auth.auth import generate_token, auth_required
from schemas.CalendarSchema import CalendarResponse, CalendarRequest, EntryType
from schemas.UserSchema import UserCreateRequest, UserLoginRequest

app = Flask(__name__)

client = MongoClient('mongodb+srv://ProjectAdmin:Parano55@calendarprojectcluster.usy8q0s.mongodb.net/?retryWrites'
                     '=true&w=majority')
db = client['CalendarDb']
calendar_collection = db['CalendarCollection']
user_collection = db['UserCollection']


@app.route('/api/login', methods=['POST'])
def user_login():
    data = request.json
    if 'username' in data and 'password' in data:
        entry = UserLoginRequest(
            username=data.get('username'),
            password=data.get('password')
        )
        if login(entry):
            user_id = get_user_id(entry.username)
            if user_id:
                token = generate_token(user_id)
                return jsonify({'token': token}), 200
    return 'Unauthorized', 401


@app.route('/api/register', methods=['POST'])
def user_register():
    data = request.json
    if 'username' in data and 'password' in data and 'mail' in data:
        entry = UserCreateRequest(
            username=data.get('username'),
            mail=data.get('mail'),
            password=data.get('password')
        )
        if register(entry):
            return 'Registered successfully', 201
    return 'Bad Request', 400


@app.route('/api/logout', methods=['POST'])
def user_logout():
    return 'Logged out successfully', 200


@app.route('/api/calendar', methods=['GET'])
@auth_required
def get_all_entries(user_id):
    entries_from_db = calendar_collection.find({'user_id': user_id})
    entries = [CalendarResponse(
        _id=str(entry['_id']),
        date=entry['date'],
        entry_type=EntryType(entry['entry_type']),
        work_hours=entry.get('work_hours'),
    ) for entry in entries_from_db]
    return jsonify([entry.to_dict() for entry in entries]), 200


@app.route('/api/calendar/add', methods=['POST'])
@auth_required
def add_entry(user_id):
    data = request.json
    if 'date' in data and 'entry_type' in data:
        if data['entry_type'] in [entry_type.value for entry_type in EntryType]:
            entry = CalendarRequest(
                date=(data['date']),
                entry_type=EntryType(data['entry_type']),
                work_hours=data.get('work_hours'),
                user_id=user_id
            )
            entry_id = calendar_collection.insert_one(entry.to_dict()).inserted_id
            return jsonify(str(entry_id)), 201
    return 'Wrong data', 400


@app.route('/api/calendar/delete/<entry_id>', methods=['DELETE'])
@auth_required
def delete_entry(user_id, entry_id):
    entry_id = ObjectId(entry_id)

    if calendar_collection.delete_one({'_id': entry_id, 'user_id': user_id}).deleted_count == 1:
        return '', 204
    return 'Entry not found', 404


@app.route('/api/calendar/getById/<entry_id>', methods=['GET'])
@auth_required
def get_entry(user_id, entry_id):
    entry_id = ObjectId(entry_id)
    entry = calendar_collection.find_one({'_id': entry_id, 'user_id': user_id})
    if entry:
        calendar_response = CalendarResponse(
            _id=str(entry['_id']),
            date=entry['date'],
            entry_type=EntryType(entry['entry_type']),
            work_hours=entry.get('work_hours')
        )
        return jsonify(calendar_response.to_dict()), 200
    return 'Entry not found', 404


@app.route('/api/calendar/update/<entry_id>', methods=['PUT'])
@auth_required
def edit_entry(user_id, entry_id):
    data = request.json
    if 'date' in data and 'entry_type' in data:
        if data['entry_type'] in [entry_type.value for entry_type in EntryType]:
            entry = CalendarRequest(
                date=datetime.strptime(data['date'], '%Y-%m-%d'),
                entry_type=EntryType(data['entry_type']),
                work_hours=data.get('work_hours'),
                user_id=user_id
            )
            result = calendar_collection.update_one({'_id': entry_id, 'user_id': user_id}, {'$set': entry.to_dict()})
            if result.modified_count == 1:
                return '', 204
    return 'Wrong data', 400


# NON CRUD METHODS
def register(user):
    if not user_exists(user.username):
        user_collection.insert_one(user.to_dict())
        return True
    return False


def user_exists(username):
    return user_collection.find_one({'username': username}) is not None


def login(user):
    user = user_collection.find_one(user.to_dict())
    if user:
        return True
    return False


def get_user_id(username):
    user = user_collection.find_one({'username': username})
    if user:
        return str(user.get('_id'))
    return None


if __name__ == '__main__':
    app.run(debug=True)
