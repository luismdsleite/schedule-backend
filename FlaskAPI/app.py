import os
import pymysql
import bcrypt
from http import HTTPStatus
from flask_cors import CORS
from flask import Flask, redirect, request, jsonify, url_for, abort
from db import Database
from config import ProductionConfig as conf
from json_provider import UpdatedJSONProvider
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager
import datetime

host = os.environ.get('FLASK_SERVER_HOST', conf.HOST)
port = os.environ.get('FLASK_SERVER_PORT', conf.PORT)
version = str(conf.VERSION).lower()
url_prefix = str(conf.URL_PREFIX).lower()
route_prefix = f"/{url_prefix}/{version}"


def create_app():
    app = Flask(__name__)
    cors = CORS(app, resources={f"{route_prefix}/*": {"origins": "*"}})
    app.config.from_object(conf)
    
    return app


def get_response_msg(data, status_code):
    message = {
        'status': status_code,
        # 'data': data if data else 'No records found'
        'data': data if data else []
    }

    response_msg = jsonify(message)

    response_msg.status_code = status_code
    return response_msg


app = create_app()
jwt = JWTManager(app)

# assign to an app instance
app.json = UpdatedJSONProvider(app)
wsgi_app = app.wsgi_app


# ==============================================[ Routes - Start ]


@app.route(f"{route_prefix}/register", methods=["POST"])
@jwt_required()
def register():
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    # Generate a salt and hash the password
    salt = bcrypt.gensalt()  # Generates a new salt
    hashed_password = bcrypt.hashpw(
        (password + conf.PEPPER).encode('utf-8'), salt)
    query = f"INSERT INTO USER(Username, PasswordHash, Salt, Hash) VALUES (%s, %s, %s, %s)"
    params = [username, hashed_password, salt, "bcrypt"]
    db = Database(conf)
    records = db.run_query(query=query, args=tuple(params))
    db.close_connection()
    response = get_response_msg(records, HTTPStatus.OK)
    return response

# Create a route to authenticate your users and return JWTs. The
# create_access_token() function is used to actually generate the JWT.


@app.route(f"{route_prefix}/login", methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    db = Database(conf)
    query = "SELECT PasswordHash, Salt FROM USER WHERE Username = %s"
    records = db.run_query(query=query, args=(username,))
    db.close_connection()

    if len(records) == 0:
        response = jsonify({"message": "User not found"}
                           ), HTTPStatus.UNAUTHORIZED
        return response

    stored_hashed_password = records[0]["PasswordHash"]
    salt = records[0]["Salt"]

    # Don't forget to add the pepper
    entered_password = (password + conf.PEPPER).encode('utf-8')
    hashed_password_to_check = bcrypt.hashpw(entered_password, salt)

    if hashed_password_to_check == stored_hashed_password:
        access_token = create_access_token(identity=username)
        response = jsonify(access_token=access_token), HTTPStatus.OK

    else:
        response = jsonify({"message": "Invalid credentials"}
                           ), HTTPStatus.UNAUTHORIZED

    return response


# /api/v1/events

@app.route(f"{route_prefix}/events", methods=['GET'])
@jwt_required()
def getEvents():
    try:
        db = Database(conf)
        # db.ping() # reconnecting mysql
        query = f"SELECT * FROM EVENT"
        records = db.run_query(query=query)
        response = get_response_msg(records, HTTPStatus.OK)

        db.close_connection()
        return response
    except pymysql.MySQLError as sqle:
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=str(sqle))
    except Exception as e:
        abort(HTTPStatus.BAD_REQUEST, description=str(e))

# /api/v1/occupations


@app.route(f"{route_prefix}/occupations", methods=['GET'])
@jwt_required()
def getOccupations():
    try:
        db = Database(conf)
        query = f"SELECT * FROM OCUPATION"
        records = db.run_query(query=query)
        response = get_response_msg(records, HTTPStatus.OK)

        db.close_connection()
        return response
    except pymysql.MySQLError as sqle:
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=str(sqle))
    except Exception as e:
        abort(HTTPStatus.BAD_REQUEST, description=str(e))

# /api/v1/restrictions


@app.route(f"{route_prefix}/restrictions", methods=['GET'])
@jwt_required()
def getRestrictions():
    try:
        db = Database(conf)
        query = f"SELECT * FROM RESTRICTION"
        records = db.run_query(query=query)
        response = get_response_msg(records, HTTPStatus.OK)

        db.close_connection()
        return response
    except pymysql.MySQLError as sqle:
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=str(sqle))
    except Exception as e:
        abort(HTTPStatus.BAD_REQUEST, description=str(e))

# /api/v1/events/{Id}


@app.route(f"{route_prefix}/events/<id>", methods=['GET'])
@jwt_required()
def getEvent(id):
    try:
        db = Database(conf)
        params = []
        query = "SELECT * FROM EVENT WHERE Id = %s"
        params.append(id)
        records = db.run_query(query=query, args=tuple(params))
        if len(records) == 0:
            abort(HTTPStatus.NOT_FOUND,
                  description=f"Event with ID {id} not found")
        response = get_response_msg(records[0], HTTPStatus.OK)
        db.close_connection()
        return response
    except pymysql.MySQLError as sqle:
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=str(sqle))
    except Exception as e:
        abort(HTTPStatus.BAD_REQUEST, description=str(e))


# /api/v1/lecturers
@app.route(f"{route_prefix}/lecturers", methods=['GET'])
@jwt_required()
def getLecturers():
    try:
        db = Database(conf)
        query = f"SELECT * FROM LECTURER"
        records = db.run_query(query=query)
        response = get_response_msg(records, HTTPStatus.OK)
        db.close_connection()
        return response
    except pymysql.MySQLError as sqle:
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=str(sqle))
    except Exception as e:
        abort(HTTPStatus.BAD_REQUEST, description=str(e))


# /api/v1/rooms
@app.route(f"{route_prefix}/rooms", methods=['GET'])
@jwt_required()
def getRooms():
    try:
        db = Database(conf)
        query = f"SELECT * FROM ROOM"
        records = db.run_query(query=query)
        response = get_response_msg(records, HTTPStatus.OK)
        db.close_connection()
        return response
    except pymysql.MySQLError as sqle:
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=str(sqle))
    except Exception as e:
        abort(HTTPStatus.BAD_REQUEST, description=str(e))


# /api/v1/blocks
@app.route(f"{route_prefix}/blocks", methods=['GET'])
@jwt_required()
def getBlocks():
    try:
        db = Database(conf)
        query = f"""
        SELECT
            b.Id AS Id, 
            b.Name AS Name,
            b.NameAbbr as NameAbbr,
            b.Hide as Hide,
            GROUP_CONCAT(be.EventId) AS AssociatedEventIds
        FROM 
            BLOCK b
        LEFT JOIN 
            BLOCK_TO_EVENT be ON b.Id = be.BlockId
        GROUP BY 
            b.Id, b.Name;
        """
        records = db.run_query(query=query)
        for record in records:
            try:
                record['AssociatedEventIds'] = [
                    int(event_id) for event_id in record['AssociatedEventIds'].split(',')]
            except:
                # case where record['AssociatedEventIds'] = null
                record['AssociatedEventIds'] = []
        response = get_response_msg(records, HTTPStatus.OK)

        db.close_connection()
        return response
    except pymysql.MySQLError as sqle:
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=str(sqle))
    except Exception as e:
        abort(HTTPStatus.BAD_REQUEST, description=str(e))


# /api/v1/lecturers
@app.route(f"{route_prefix}/lecturers", methods=['POST'])
@jwt_required()
def createLecturer():
    try:
        db = Database(conf)
        body = request.get_json()
        name = body['Name']
        nameAbbr = body['NameAbbr']
        office = body['Office']
        hide = body['Hide']
        params = [name, nameAbbr, office, hide]
        query = f"INSERT INTO LECTURER(Name, NameAbbr, Office, Hide) VALUES (%s, %s, %s, %s)"
        records = db.run_query(query=query, args=tuple(params))
        response = get_response_msg(records,  HTTPStatus.OK)
        db.close_connection()
        return response
    except pymysql.MySQLError as sqle:
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=str(sqle))
    except Exception as e:
        abort(HTTPStatus.BAD_REQUEST, description=str(e))



# /api/v1/rooms
@app.route(f"{route_prefix}/rooms", methods=['POST'])
@jwt_required()
def createRoom():
    try:
        db = Database(conf)
        body = request.get_json()
        name = body['Name']
        nameAbbr = body['NameAbbr']
        number = body['Number']
        capacity = body['Capacity']
        hide = body['Hide']
        params = [name, nameAbbr, number, capacity, hide]
        query = f"INSERT INTO ROOM(Name, NameAbbr, Number, Capacity, Hide) VALUES (%s, %s, %s, %s, %s)"
        records = db.run_query(query=query, args=tuple(params))
        response = get_response_msg(records,  HTTPStatus.OK)
        db.close_connection()
        return response
    except pymysql.MySQLError as sqle:
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=str(sqle))
    except Exception as e:
        abort(HTTPStatus.BAD_REQUEST, description=str(e))

# /api/v1/events
@app.route(f"{route_prefix}/events", methods=['POST'])
@jwt_required()
def createEvent():
    try:
        db = Database(conf)
        body = request.get_json()
        query_part1 = "INSERT INTO EVENT (Subject, SubjectAbbr, "
        query_part2 = ") VALUES (%s, %s, "
        params = [body['Subject'], body['SubjectAbbr']]

        if 'StartTime' in body:
            query_part1 += " StartTime,"
            query_part2 += " %s,"
            params.append(body['StartTime'])
        if 'EndTime' in body:
            query_part1 += " EndTime,"
            query_part2 += " %s,"
            params.append(body['EndTime'])
        if 'WeekDay' in body:
            query_part1 += " WeekDay,"
            query_part2 += " %s,"
            params.append(body['WeekDay'])
        if 'RoomId' in body:
            query_part1 += " RoomId,"
            query_part2 += " %s,"
            params.append(body['RoomId'])
        if 'LecturerId' in body:
            query_part1 += " LecturerId,"
            query_part2 += " %s,"
            params.append(body['LecturerId'])
        if 'Hide' in body:
            query_part1 += " Hide,"
            query_part2 += " %s,"
            params.append(body['Hide'])
        query = query_part1[:-1] + query_part2[:-1] + ")"
        records = db.run_query(query=query, args=tuple(params))
        response = get_response_msg(records,  HTTPStatus.OK)
        db.close_connection()
        return response
    except pymysql.MySQLError as sqle:
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=str(sqle))
    except Exception as e:
        abort(HTTPStatus.BAD_REQUEST, description=str(e))

@app.route(f"{route_prefix}/events/<id>", methods=['PUT'])
@jwt_required()
def updateEvent(id):
    try:
        db = Database(conf)
        body = request.get_json()
        query = "UPDATE EVENT SET Subject = %s, SubjectAbbr = %s,"
        params = [body['Subject'], body['SubjectAbbr']]
        if 'StartTime' in body:
            query += " StartTime = %s,"
            params.append(body['StartTime'])
        if 'EndTime' in body:
            query += " EndTime = %s,"
            params.append(body['EndTime'])
        if 'WeekDay' in body:
            query += " WeekDay = %s,"
            params.append(body['WeekDay'])
        if 'RoomId' in body:
            query += " RoomId = %s,"
            params.append(body['RoomId'])
        if 'LecturerId' in body:
            query += " LecturerId = %s,"
            params.append(body['LecturerId'])
        if 'Hide' in body:
            query += " Hide = %s,"
            params.append(body['Hide'])
        query = query[:-1] + " WHERE Id = %s"
        params.append(id)

        records = db.run_query(query=query, args=tuple(params))
        response = get_response_msg(records,  HTTPStatus.OK)
        db.close_connection()
        return response
    except pymysql.MySQLError as sqle:
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=str(sqle))
    except Exception as e:
        abort(HTTPStatus.BAD_REQUEST, description=str(e))


# /api/v1/rooms/<id>
@app.route(f"{route_prefix}/rooms/<id>", methods=['DELETE'])
@jwt_required()
def deleteRoom(id):
    try:
        db = Database(conf)
        query = f"DELETE FROM ROOM WHERE Id=%s"
        params = [id]
        records = db.run_query(query=query, args=tuple(params))
        response = get_response_msg(records,  HTTPStatus.OK)
        db.close_connection()
        return response
    except pymysql.MySQLError as sqle:
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=str(sqle))
    except Exception as e:
        abort(HTTPStatus.BAD_REQUEST, description=str(e))


# /api/v1/lecturers/<id>
@app.route(f"{route_prefix}/lecturers/<id>", methods=['DELETE'])
@jwt_required()
def deleteLecturer(id):
    try:
        db = Database(conf)
        query = f"DELETE FROM LECTURER WHERE Id=%s"
        params = [id]
        records = db.run_query(query=query, args=tuple(params))
        response = get_response_msg(records,  HTTPStatus.OK)
        db.close_connection()
        return response
    except pymysql.MySQLError as sqle:
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=str(sqle))
    except Exception as e:
        abort(HTTPStatus.BAD_REQUEST, description=str(e))


# /api/v1/health
@app.route(f"{route_prefix}/health", methods=['GET'])
def health():
    try:
        db = Database(conf)
        db_status = "Connected to DB" if db.db_connection_status else "Not connected to DB"
        response = get_response_msg("I am fine! " + db_status, HTTPStatus.OK)
        db.close_connection()
        return response
    except pymysql.MySQLError as sqle:
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=str(sqle))
    except Exception as e:
        abort(HTTPStatus.BAD_REQUEST, description=str(e))

# /


@app.route('/', methods=['GET'])
def home():
    return redirect(url_for('health'))

# =================================================[ Routes - End ]

# ================================[ Error Handler Defined - Start ]
# HTTP 404 error handler


@app.errorhandler(HTTPStatus.NOT_FOUND)
def page_not_found(e):
    return get_response_msg(data=str(e), status_code=HTTPStatus.NOT_FOUND)


# HTTP 400 error handler
@app.errorhandler(HTTPStatus.BAD_REQUEST)
def bad_request(e):
    return get_response_msg(str(e), HTTPStatus.BAD_REQUEST)


# HTTP 500 error handler
@app.errorhandler(HTTPStatus.INTERNAL_SERVER_ERROR)
def internal_server_error(e):
    return get_response_msg(str(e), HTTPStatus.INTERNAL_SERVER_ERROR)
# ==================================[ Error Handler Defined - End ]


if __name__ == '__main__':
    # Launch the application
    app.run(ssl_context=('certs/cert.pem', 'certs/key.pem'), host=host, port=port)
