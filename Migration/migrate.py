"""
This script migrates the data from the old database to the new database. It reads the old DB data (stored in the old_db folder in CSV format), converts it to the new format and writes it to the new database. The data is also written to CSV files in the new_db folder.
"""
import sys
import pandas as pd
import os
from dotenv import load_dotenv
import mysql.connector
from time_converter import convertTime
import numpy as np
import traceback

# Load environment variables from .env file
load_dotenv()

old_db_folder = "old_db/"
new_db_folder = "new_db/"

# Connect to MySQL database using environment variables
db_config = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME'),
}

connection = mysql.connector.connect(**db_config)
cursor = connection.cursor()


def migrateRooms(cursor):
    input_file = old_db_folder + "Salas.csv"
    output_file = new_db_folder + "Rooms.csv"

    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(input_file)
    df.rename(columns={"id": "Id", "nome": "Name", "abreviatura": "NameAbbr",
              "numero": "Number", "capacidade": "Capacity", "ocultar": "Hide"}, inplace=True)
    df['Hide'] = df['Hide'].replace({False: 0, True: 1})
    df['Number'] = df['Number'].astype(str)
    df['Number'] = df['Number'].replace({'nan': ''})

    df.to_csv(output_file, index=False)
    # Insert data into the ROOM table
    insert_query = '''
    INSERT INTO ROOM (Id, NameAbbr, Name, Number, Capacity, Hide)
    VALUES (%s, %s, %s, %s, %s, %s);
    '''

    for index, row in df.iterrows():
        values = (row['Id'], row['NameAbbr'], row['Name'],
                  row['Number'], row['Capacity'], row['Hide'])
        cursor.execute(insert_query, values)
        connection.commit()


def migrateLecturers(cursor):
    input_file = old_db_folder + "Docentes.csv"
    output_file = new_db_folder + "Lecturers.csv"

    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(input_file)
    df.rename(columns={"id": "Id", "nome": "Name", "abreviatura": "NameAbbr",
              "gabinete": "Office", "ocultar": "Hide"}, inplace=True)
    df['Hide'] = df['Hide'].replace({False: 0, True: 1})
    df['Office'] = df['Office'].astype(str)
    df['Office'] = df['Office'].replace({'nan': ''})

    df.to_csv(output_file, index=False)
    # Insert data into the LECTURER table
    insert_query = '''
    INSERT INTO LECTURER (Id, NameAbbr, Name, Office, Hide)
    VALUES (%s, %s, %s, %s, %s);
    '''

    for index, row in df.iterrows():
        values = (row['Id'], row['NameAbbr'],
                  row['Name'], row['Office'], row['Hide'])
        cursor.execute(insert_query, values)
        connection.commit()


def migrateRestrictions(cursor):
    input_file = old_db_folder + "Restricoes.csv"
    output_file = new_db_folder + "Restrictions.csv"

    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(input_file)
    df.rename(columns={"id": "Id", "docente_id": "LecturerId",
              "tipo": "Type", "dia": "Weekday"}, inplace=True)
    # convert the "hora" and "duração" columns to "StartTime" and "Endtime columns"
    df = convertTime(df)

    df.to_csv(output_file, index=False)
    # Insert data into the RESTRICTION table
    insert_query = '''
    INSERT INTO RESTRICTION (Id, LecturerId, Type, Weekday, StartTime, EndTime)
    VALUES (%s, %s, %s, %s, %s, %s);
    '''

    for index, row in df.iterrows():
        values = (row['Id'], row['LecturerId'], row['Type'],
                  row['Weekday'], row['StartTime'], row['EndTime'])
        cursor.execute(insert_query, values)
        connection.commit()


def migrateEvents(cursor):
    input_file = old_db_folder + "Cadeiras.csv"
    output_file = new_db_folder + "Events.csv"

    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(input_file)
    df.rename(columns={"id": "Id", "nome": "Subject", "abreviatura": "SubjectAbbr",
              "docente_id": "LecturerId", "sala_id": "RoomId", "dia": "WeekDay", "ocultar": "Hide"}, inplace=True)

    df['Hide'] = df['Hide'].replace({False: 0, True: 1})
    # convert the "hora" and "duração" columns to "StartTime" and "Endtime columns"
    df = convertTime(df)

    df = df.replace(np.nan, None)

    # print(df)
    df.to_csv(output_file, index=False)
    # Insert data into the EVENT table
    insert_query = '''
    INSERT INTO EVENT (Id, Subject, SubjectAbbr, LecturerId, RoomId, StartTime, EndTime, WeekDay, Hide)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
    '''

    for index, row in df.iterrows():
        values = (row['Id'], row['Subject'], row['SubjectAbbr'], row['LecturerId'], row['RoomId'],
                  row['StartTime'], row['EndTime'], row['WeekDay'], row['Hide'])
        cursor.execute(insert_query, values)
        connection.commit()


def migrateBlocks(cursor):
    input_file = old_db_folder + "Blocos.csv"
    output_file = new_db_folder + "Blocks.csv"

    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(input_file)
    df.rename(columns={"id": "Id", "nome": "Name", "abreviatura": "NameAbbr",
              "ocultar": "Hide"}, inplace=True)
    df['Hide'] = df['Hide'].replace({False: 0, True: 1})

    df.to_csv(output_file, index=False)
    # Insert data into the BLOCK table
    insert_query = '''
    INSERT INTO BLOCK (Id, NameAbbr, Name, Hide)
    VALUES (%s, %s, %s, %s);
    '''

    for index, row in df.iterrows():
        values = (row['Id'], row['NameAbbr'], row['Name'], row['Hide'])
        cursor.execute(insert_query, values)
        connection.commit()


def migrateBlockToEvent(cursor):
    input_file = old_db_folder + "Cadeiras por Bloco.csv"
    output_file = new_db_folder + "BlockToEvent.csv"

    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(input_file)
    df.rename(columns={"bloco_id": "BlockId",
              "cadeira_id": "EventId"}, inplace=True)
        
    df.to_csv(output_file, index=False)
    # Insert data into the BLOCK table
    insert_query = '''
    INSERT INTO BLOCK_TO_EVENT(BlockId, EventId)
    VALUES (%s, %s);
    '''

    for index, row in df.iterrows():
        values = (int(row['BlockId']), int(row['EventId']))
        cursor.execute(insert_query, values)
        connection.commit()

exit_code = 0
try:
    migrateRooms(cursor)
except Exception as e:
    traceback.print_exc()
    exit_code = 1
try:    
    migrateLecturers(cursor)
except Exception as e:
    traceback.print_exc()
    exit_code = 1
try:    
    migrateRestrictions(cursor)
except Exception as e:
    traceback.print_exc()
    exit_code = 1
try:    
    migrateEvents(cursor)
except Exception as e:
    traceback.print_exc()
    exit_code = 1
try:    
    migrateBlocks(cursor)
except Exception as e:
    traceback.print_exc()
    exit_code = 1
try:    
    migrateBlockToEvent(cursor)
except Exception as e:
    traceback.print_exc()
    exit_code = 1

# Close the connection
cursor.close()
connection.close()
sys.exit(exit_code)