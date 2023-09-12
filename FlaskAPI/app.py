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
import pymysql.cursors



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

# Route for getting a specific block by ID
@app.route(f"{route_prefix}/blocks/<id>", methods=['GET'])
@jwt_required()
def getBlock(id):
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
        WHERE
            b.id = %s
        GROUP BY 
            b.Id, b.Name;
        """
        records = db.run_query(query=query, args=(id))
        for record in records:
            try:
                record['AssociatedEventIds'] = [
                    int(event_id) for event_id in record['AssociatedEventIds'].split(',')]
            except:
                # case where record['AssociatedEventIds'] = null
                record['AssociatedEventIds'] = []
        response = get_response_msg(records[0], HTTPStatus.OK)

        db.close_connection()
        return response
    except pymysql.MySQLError as sqle:
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=str(sqle))
    except Exception as e:
        abort(HTTPStatus.BAD_REQUEST, description=str(e))

# /api/v1/rooms
@app.route(f"{route_prefix}/rooms/<id>", methods=['GET'])
@jwt_required()
def getRoom(id):
    try:
        db = Database(conf)
        query = f"SELECT * FROM ROOM WHERE Id = %s"
        records = db.run_query(query=query, args=(id))
        response = get_response_msg(records[0], HTTPStatus.OK)
        db.close_connection()
        return response
    except pymysql.MySQLError as sqle:
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=str(sqle))
    except Exception as e:
        abort(HTTPStatus.BAD_REQUEST, description=str(e))

# /api/v1/lecturers
@app.route(f"{route_prefix}/lecturers/<id>", methods=['GET'])
@jwt_required()
def getLecturer(id):
    try:
        db = Database(conf)
        query = f"SELECT * FROM LECTURER WHERE Id = %s"
        records = db.run_query(query=query, args=(id))
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

# Route for creating a new block via POST request
@app.route(f"{route_prefix}/blocks", methods=['POST'])
@jwt_required()
def createBlock():
    try:
        # Parse the JSON data from the POST request
        data = request.get_json()

        # Create a database connection
        db = Database(conf)
        conn = db.get_connection()

        # Insert a new block into the database
        query = """
        INSERT INTO BLOCK (Name, NameAbbr, Hide)
        VALUES (%s, %s, %s)
        """
        cursor = conn.cursor()
        cursor.execute(query, (data['Name'], data['NameAbbr'], data['Hide']))

        # Retrieve the ID of the newly created block
        new_block_id = cursor.lastrowid

        # Update the block's associated events
        if 'AssociatedEventIds' in data:
            insert_query = """
            INSERT INTO BLOCK_TO_EVENT (BlockId, EventId)
            VALUES (%s, %s)
            """
            for event_id in data['AssociatedEventIds']:
                cursor.execute(insert_query, (new_block_id, event_id))

        # Commit the changes to the database
        conn.commit()

        # Close the cursor and database connection
        db.close_connection()

        return getBlock(new_block_id), HTTPStatus.CREATED

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
        db.close_connection()
        return getLecturer(records['id'])
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
        return getRoom(records['id'])
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
        db.close_connection()
        return getEvent(records['id'])
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

        query += " StartTime = %s,"
        params.append(body['StartTime'])

        query += " EndTime = %s,"
        params.append(body['EndTime'])

        query += " WeekDay = %s,"
        params.append(body['WeekDay'])

        query += " RoomId = %s,"
        params.append(body['RoomId'])

        query += " LecturerId = %s,"
        params.append(body['LecturerId'])

        query += " Hide = %s,"
        params.append(body['Hide'])
        query = query[:-1] + " WHERE Id = %s"
        params.append(id)

        records = db.run_query(query=query, args=tuple(params))
        response = get_response_msg(records,  HTTPStatus.OK)
        db.close_connection()
        return getEvent(id)
    except pymysql.MySQLError as sqle:
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=str(sqle))
    except Exception as e:
        abort(HTTPStatus.BAD_REQUEST, description=str(e))

# /api/v1/rooms/<id>
@app.route(f"{route_prefix}/rooms/<id>", methods=['PUT'])
@jwt_required()
def updateRoom(id):
    try:
        db = Database(conf)
        body = request.get_json()
        params = [body['Name'], body['NameAbbr'],  body['Number'], body['Capacity'], body['Hide'], id]
        query = "UPDATE ROOM SET Name=%s, NameAbbr=%s, Number=%s, Capacity=%s, HIDE=%s WHERE Id = %s"
        records = db.run_query(query=query, args=tuple(params))
        response = get_response_msg(records,  HTTPStatus.OK)
        db.close_connection()
        return getRoom(id)
    except pymysql.MySQLError as sqle:
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=str(sqle))
    except Exception as e:
        abort(HTTPStatus.BAD_REQUEST, description=str(e))

# /api/v1/lecturers/<id>
@app.route(f"{route_prefix}/lecturers/<id>", methods=['PUT'])
@jwt_required()
def updateLect(id):
    try:
        db = Database(conf)
        body = request.get_json()
        params = [body['Name'], body['NameAbbr'],  body['Office'], body['Hide'], id]
        query = "UPDATE LECTURER SET Name=%s, NameAbbr=%s, Office=%s, HIDE=%s WHERE Id = %s"
        records = db.run_query(query=query, args=tuple(params))
        response = get_response_msg(records,  HTTPStatus.OK)
        db.close_connection()
        return getLecturer(id)
    except pymysql.MySQLError as sqle:
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=str(sqle))
    except Exception as e:
        abort(HTTPStatus.BAD_REQUEST, description=str(e))


# /api/v1/blocks/<id>
@app.route(f"{route_prefix}/blocks/<id>", methods=['PUT'])
@jwt_required()
def updateBlock(id):
    try:
        # Parse the JSON data from the PUT request
        data = request.get_json()

        # Create a database connection
        db = Database(conf)
        conn = db.get_connection()

        # Update the block's information
        query = """
        UPDATE BLOCK
        SET Name = %s, NameAbbr = %s, Hide = %s
        WHERE Id = %s
        """
        cursor = conn.cursor()
        cursor.execute(query, (data['Name'], data['NameAbbr'], data['Hide'], id))

        # Update the block's associated events
        if 'AssociatedEventIds' in data:
            # First, delete all existing associations for the block
            delete_query = """
            DELETE FROM BLOCK_TO_EVENT
            WHERE BlockId = %s
            """
            cursor.execute(delete_query, (id))

            # Then, add the new associations
            insert_query = """
            INSERT INTO BLOCK_TO_EVENT (BlockId, EventId)
            VALUES (%s, %s)
            """
            for event_id in data['AssociatedEventIds']:
                cursor.execute(insert_query, (id, event_id))

        # Commit the changes to the database
        conn.commit()

        # Close the cursor and database connection
        db.close_connection()

        return getBlock(id)

    except pymysql.MySQLError as sqle:
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=str(sqle))
    except Exception as e:
        abort(HTTPStatus.BAD_REQUEST, description=str(e))

# /api/v1/blocks/<id>
@app.route(f"{route_prefix}/blocks/<id>", methods=['DELETE'])
@jwt_required()
def deleteBlock(id):
    try:
        # Create a database connection
        db = Database(conf)
        conn = db.get_connection()

        cursor = conn.cursor()

        # First, delete all existing associations for the block
        delete_block_to_events_query = """
        DELETE FROM BLOCK_TO_EVENT
        WHERE BlockId = %s
        """
        cursor.execute(delete_block_to_events_query, (id))
        print("Reached")
        # Then, delete the block
        delete_block_query = """
        DELETE FROM BLOCK WHERE Id =%s
        """
        cursor.execute(delete_block_query, (id))

        # Commit the changes to the database
        conn.commit()

        # Close the cursor and database connection
        db.close_connection()

        return get_response_msg({}, HTTPStatus.OK)

    except pymysql.MySQLError as sqle:
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=str(sqle))
    except Exception as e:
        abort(HTTPStatus.BAD_REQUEST, description=str(e))

# /api/v1/events/<id>
@app.route(f"{route_prefix}/events/<id>", methods=['DELETE'])
@jwt_required()
def deleteEvent(id):
    try:
        db = Database(conf)
        query = f"DELETE FROM EVENT WHERE Id=%s"
        params = [id]
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
