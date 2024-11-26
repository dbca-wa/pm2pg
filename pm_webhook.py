import urllib3
from urllib3.exceptions import InsecureRequestWarning  # for insecure https warnings
urllib3.disable_warnings(InsecureRequestWarning)  # disable insecure https warnings
import json
import psycopg2
from flask import Flask, request
# from flask_basicauth import BasicAuth
import os

# WEBHOOK_USERNAME = os.getenv('WEBHOOK_USERNAME')
# WEBHOOK_PASSWORD = os.getenv('WEBHOOK_PASSWORD')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
TABLE_NAME = os.getenv('TABLE_NAME') 
save_webhook_output_file = "webhooklogs.json"

app = Flask(__name__)

# app.config['BASIC_AUTH_USERNAME'] = WEBHOOK_USERNAME
# app.config['BASIC_AUTH_PASSWORD'] = WEBHOOK_PASSWORD
# app.config['BASIC_AUTH_FORCE'] = True

# basic_auth = BasicAuth(app)

@app.route('/') 
# @basic_auth.required
def index():
    return '<h1>Im Alive</h1>', 200

@app.route('/api', methods=['POST'])  
# @basic_auth.required
def webhook():
    if request.method == 'POST':
        print('Webhook Received')
        request_json = request.json
        request_json['Details'] = request_json.get('Details', 0)
        request_json['Content'] = request_json.get('Content', 0)
        print('Payload: ')
        print(json.dumps(request_json, indent=4))

        with open(save_webhook_output_file, 'a') as filehandle:
            filehandle.write('%s\n' % json.dumps(request_json, indent=4))
            filehandle.write('= - = - = - = - = - = - = - = - = - = - = - = - = - = - = - = - = - = - \n')

        try:
            connection = psycopg2.connect(
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                host=DB_HOST,
                port=DB_PORT
            )
            cursor = connection.cursor()
            insert_query = f"""
            INSERT INTO {TABLE_NAME} (ID, Type, RecordType, TypeCode, Tag, MessageID, Email, fromaddress, BouncedAt, Inactive, DumpAvailable, CanActivate, Subject, ServerID, MessageStream, Name, Description, Metadata, Details, Content)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                request_json.get('ID'),
                request_json.get('Type'),
                request_json.get('RecordType'),
                request_json.get('TypeCode'),
                request_json.get('Tag'),
                request_json.get('MessageID'),
                request_json.get('Email'),
                request_json.get('From'),
                request_json.get('BouncedAt'),
                request_json.get('Inactive'),
                request_json.get('DumpAvailable'),
                request_json.get('CanActivate'),
                request_json.get('Subject'),
                request_json.get('ServerID'),
                request_json.get('MessageStream'),
                request_json.get('Name'),
                request_json.get('Description'),
                request_json.get('Metadata'),
                request_json.get('Details'),
                request_json.get('Content')
            ))
            connection.commit()
        except Exception as e:
            print(f"Error inserting into database: {e}")
            return 'Internal Server Error', 500
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

        return 'Webhook notification received', 202
    else:
        return 'POST Method not supported', 405

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5443, debug=True, ssl_context=('cert.pem', 'key.pem'))
