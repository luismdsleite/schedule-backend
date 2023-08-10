import os
import pymysql
from http import HTTPStatus
from flask_cors import CORS
from flask import Flask, redirect, request, jsonify, url_for, abort
from db import Database
from config import DevelopmentConfig as devconf
from json_provider import UpdatedJSONProvider


host = os.environ.get('FLASK_SERVER_HOST', devconf.HOST)
port = os.environ.get('FLASK_SERVER_PORT', devconf.PORT)
version = str(devconf.VERSION).lower()
url_prefix = str(devconf.URL_PREFIX).lower()
route_prefix = f"/{url_prefix}/{version}"


def create_app():
    app = Flask(__name__)
    cors = CORS(app, resources={f"{route_prefix}/*": {"origins": "*"}})
    app.config.from_object(devconf)
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
# assign to an app instance
app.json = UpdatedJSONProvider(app)
wsgi_app = app.wsgi_app
db = Database(devconf)

# ==============================================[ Routes - Start ]


# /api/v1/events
@app.route(f"{route_prefix}/events", methods=['GET'])
def getEvents():
    try:
        query = f"SELECT * FROM EVENT"
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
def getEvent(id):
    try:
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
def getLecturers():
    try:
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
def getRooms():
    try:
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
def getBlocks():
    try:
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
                record['AssociatedEventIds'] = [int(event_id) for event_id in record['AssociatedEventIds'].split(',')]
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
def createLecturer():
    try:
        body = request.get_json()
        name = body['name']
        nameAbbr = body['nameAbbr']
        office = body['office']
        hide = body['hide']
        query = f"INSERT INTO LECTURER(Name, NameAbbr, Office, Hide) VALUES ('{name}', '{nameAbbr}', '{office}', {hide})"
        records = db.run_query(query=query)
        response = get_response_msg(records,  HTTPStatus.OK)
        db.close_connection()
        return response
    except pymysql.MySQLError as sqle:
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=str(sqle))
    except Exception as e:
        abort(HTTPStatus.BAD_REQUEST, description=str(e))


# /api/v1/rooms
@app.route(f"{route_prefix}/rooms", methods=['POST'])
def createRoom():
    try:
        body = request.get_json()
        name = body['name']
        nameAbbr = body['nameAbbr']
        number = body['number']
        capacity = body['capacity']
        hide = body['hide']
        query = f"INSERT INTO ROOM(Name, NameAbbr, Number, Capacity, Hide) VALUES ('{name}', '{nameAbbr}', '{number}', {capacity}, {hide})"
        records = db.run_query(query=query)
        response = get_response_msg(records,  HTTPStatus.OK)
        db.close_connection()
        return response
    except pymysql.MySQLError as sqle:
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=str(sqle))
    except Exception as e:
        abort(HTTPStatus.BAD_REQUEST, description=str(e))


@app.route(f"{route_prefix}/events/<id>", methods=['PUT'])
def updateEvent(id):
    try:
        body = request.get_json()
        query = "UPDATE EVENT SET"
        params = []
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
def deleteRoom(id):
    try:
        query = f"DELETE FROM ROOM WHERE Id={id}"
        records = db.run_query(query=query)
        response = get_response_msg(records,  HTTPStatus.OK)
        db.close_connection()
        return response
    except pymysql.MySQLError as sqle:
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description=str(sqle))
    except Exception as e:
        abort(HTTPStatus.BAD_REQUEST, description=str(e))


# /api/v1/lecturers/<id>
@app.route(f"{route_prefix}/lecturers/<id>", methods=['DELETE'])
def deleteLecturer(id):
    try:
        query = f"DELETE FROM LECTURER WHERE Id={id}"
        records = db.run_query(query=query)
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
        db_status = "Connected to DB" if db.db_connection_status else "Not connected to DB"
        response = get_response_msg("I am fine! " + db_status, HTTPStatus.OK)
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
