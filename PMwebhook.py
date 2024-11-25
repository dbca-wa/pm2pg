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
save_webhook_output_file = "webhooklogs.json"

app = Flask(__name__)

# app.config['BASIC_AUTH_USERNAME'] = WEBHOOK_USERNAME
# app.config['BASIC_AUTH_PASSWORD'] = WEBHOOK_PASSWORD
# app.config['BASIC_AUTH_FORCE'] = True

# Establish database connection
connection = psycopg2.connect(
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME,
    host=DB_HOST,
    port=DB_PORT
)
print("Database connection to {} successful".format(DB_NAME))


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

        print('Payload: ')
        print(json.dumps(request_json,indent=4))


        with open(save_webhook_output_file, 'a') as filehandle:
            filehandle.write('%s\n' % json.dumps(request_json,indent=4))
            filehandle.write('= - = - = - = - = - = - = - = - = - = - = - = - = - = - = - = - = - = - \n')

        return 'Webhook notification received', 202
    else:
        return 'POST Method not supported', 405

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5443, debug=True)
