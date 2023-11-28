from bson import ObjectId
from flasgger import Swagger
from flask import Flask
from flask import request, jsonify
from flask_cors import CORS
from pymongo import MongoClient

from auth.auth import generate_token, auth_required
from schemas.CalendarSchema import CalendarResponse, CalendarRequest, EntryType
from schemas.UserSchema import UserCreateRequest, UserLoginRequest

app = Flask(__name__)
CORS(app)
swagger = Swagger(app)

client = MongoClient('mongodb+srv://ProjectAdmin:Parano55@calendarprojectcluster.usy8q0s.mongodb.net/?retryWrites'
                     '=true&w=majority')
db = client['CalendarDb']
calendar_collection = db['CalendarCollection']
user_collection = db['UserCollection']


@app.route('/api/login', methods=['POST'])
def user_login():
    """
        User Login Endpoint
        ---
        summary: Authenticate a user and generate a token
        tags:
          - Calendar
        parameters:
          - name: username
            in: body
            type: string
            required: true
            description: The username of the user.
          - name: password
            in: body
            type: string
            required: true
            description: The password of the user.
        responses:
          200:
            description: Successful login. Returns a JWT token.
            schema:
              type: object
              properties:
                token:
                  type: string
                  description: JWT token for authentication.
            examples:
              {'token': 'your_generated_token_here'}
          401:
            description: Unauthorized. Invalid credentials.
        """
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
    """
        User Register Endpoint
        ---
        summary: Register a new user
        tags:
          - Calendar
        parameters:
          - name: username
            in: body
            type: string
            required: true
            description: The username of the new user.
          - name: mail
            in: body
            type: string
            required: true
            description: The email address of the new user.
          - name: password
            in: body
            type: string
            required: true
            description: The password of the new user.
        responses:
          201:
            description: Registered successfully.
          400:
            description: Bad Request. Missing or invalid data.
          403:
            description: Username is already taken.
        """
    data = request.json
    if 'username' in data and 'password' in data and 'mail' in data:
        entry = UserCreateRequest(
            username=data.get('username'),
            mail=data.get('mail'),
            password=data.get('password')
        )
        if register(entry):
            return 'Registered successfully', 201
        else:
            return 'Username taken', 403
    return 'Bad Request', 400


@app.route('/api/calendar', methods=['GET'])
@auth_required
def get_all_entries(user_id):
    """
    Get All Calendar Entries Endpoint
    ---
    summary: Get all calendar entries for the authenticated user
    tags:
      - Calendar
    security:
      - BearerAuth: []
    responses:
      200:
        description: List of calendar entries.
        schema:
          type: array
          items:
            type: object
            properties:
              _id:
                type: string
              date:
                type: string
              entry_type:
                type: string
              work_hours:
                type: number
            required:
              - _id
              - date
              - entry_type
      401:
        description: Unauthorized.
    """
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
    """
    Add Calendar Entry Endpoint
    ---
    summary: Add a new calendar entry for the authenticated user
    tags:
      - Calendar
    security:
      - BearerAuth: []
    parameters:
      - name: date
        in: body
        type: string
        required: true
        description: The date of the new entry.
      - name: entry_type
        in: body
        type: string
        enum: ['work', 'business_trip', 'vacation', 'sick_leave']
        required: true
        description: >
          The type of the new entry. Should be one of: 'WORK', 'PERSONAL', 'VACATION'.
      - name: work_hours
        in: body
        type: number
        description: The number of work hours for the new entry (optional).
    responses:
      201:
        description: New entry added successfully.
        schema:
          type: object
          properties:
            entry_id:
              type: string
        examples:
          {'entry_id': 'your_generated_entry_id_here'}
      400:
        description: Bad Request. Missing or invalid data.
    """
    data = request.json
    if 'date' in data and 'entry_type' in data:
        if data['entry_type'] in [entry_type.value for entry_type in EntryType]:
            entry = CalendarRequest(
                date=(data['date']),
                entry_type=EntryType(data['entry_type']),
                work_hours=data.get('work_hours'),
                user_id=user_id
            )
            if validate_entry(entry):
                entry_id = calendar_collection.insert_one(entry.to_dict()).inserted_id
                return jsonify(str(entry_id)), 201
            else:
                return 'Invalid entry data', 400
    return 'Wrong data', 400


@app.route('/api/calendar/delete/<entry_id>', methods=['DELETE'])
@auth_required
def delete_entry(user_id, entry_id):
    """
    Delete Calendar Entry Endpoint
    ---
    summary: Delete a calendar entry for the authenticated user
    tags:
      - Calendar
    security:
      - BearerAuth: []
    parameters:
      - name: entry_id
        in: path
        type: string
        required: true
        description: The ID of the entry to be deleted.
    responses:
      204:
        description: Entry deleted successfully.
      404:
        description: Entry not found.
    """
    entry_id = ObjectId(entry_id)

    if calendar_collection.delete_one({'_id': entry_id, 'user_id': user_id}).deleted_count == 1:
        return '', 204
    return 'Entry not found', 404


@app.route('/api/calendar/getById/<entry_id>', methods=['GET'])
@auth_required
def get_entry(user_id, entry_id):
    """
    Get Calendar Entry by ID Endpoint
    ---
    summary: Get a calendar entry by ID for the authenticated user
    tags:
      - Calendar
    security:
      - BearerAuth: []
    parameters:
      - name: entry_id
        in: path
        type: string
        required: true
        description: The ID of the entry to be retrieved.
    responses:
      200:
        description: Details of the calendar entry.
        schema:
          type: object
          properties:
            _id:
              type: string
            date:
              type: string
            entry_type:
              type: string
            work_hours:
              type: number
          required:
            - _id
            - date
            - entry_type
      404:
        description: Entry not found.
    """
    entry = calendar_collection.find_one({'_id': ObjectId(entry_id), 'user_id': user_id})
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
    """
       Update Calendar Entry Endpoint
       ---
       summary: Update an existing calendar entry for the authenticated user
       tags:
         - Calendar
       security:
         - BearerAuth: []
       parameters:
         - name: entry_id
           in: path
           type: string
           required: true
           description: The ID of the entry to be updated.
         - name: date
           in: body
           type: string
           required: true
           description: The updated date of the entry.
         - name: entry_type
           in: body
           type: string
           enum: ['work', 'business_trip', 'vacation', 'sick_leave']
           required: true
           description: >
             The updated type of the entry. Should be one of: 'WORK', 'PERSONAL', 'VACATION'.
         - name: work_hours
           in: body
           type: number
           description: The updated number of work hours for the entry (optional).
       responses:
         204:
           description: Entry updated successfully.
         400:
           description: Bad Request. Missing or invalid data.
         404:
           description: Entry not found.
       """
    data = request.json
    entry = calendar_collection.find_one({'_id': ObjectId(entry_id), 'user_id': user_id})
    if entry:
        if 'date' in data and 'entry_type' in data:
            if data['entry_type'] in [entry_type.value for entry_type in EntryType]:
                entry = CalendarRequest(
                    date=(data['date']),
                    entry_type=EntryType(data['entry_type']),
                    work_hours=data.get('work_hours'),
                    user_id=user_id
                )
                if validate_entry(entry):
                    result = calendar_collection.update_one({'_id': ObjectId(entry_id)},
                                                            {'$set': entry.to_dict()})
                    if result.modified_count == 1:
                        return '', 204
                    return 'Wrong data', 400
                else:
                    return 'Invalid entry data', 400
    else:
        return 'No entry found', 404


# NON CRUD METHODS
def validate_entry(calendar_entry):
    if calendar_entry.entry_type == EntryType.WORK:
        if calendar_entry.work_hours is None:
            return False
    elif calendar_entry.work_hours is not None:
        return False
    return True


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
