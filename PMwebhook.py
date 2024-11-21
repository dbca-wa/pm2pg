import urllib3
from urllib3.exceptions import InsecureRequestWarning  # for insecure https warnings
urllib3.disable_warnings(InsecureRequestWarning)  # disable insecure https warnings
import json
import psycopg2
from flask import Flask, request
from flask_basicauth import BasicAuth
from kubernetes import client, config
import base64

# Load Kubernetes configuration
config.load_incluster_config()

# Access the secret
v1 = client.CoreV1Api()
secret = v1.read_namespaced_secret("pm2pg-secrets", "pm2pg")

WEBHOOK_USERNAME = base64.b64decode(secret.data['username']).decode('utf-8')
WEBHOOK_PASSWORD = base64.b64decode(secret.data['password']).decode('utf-8')
DB_USER = base64.b64decode(secret.data['db_user']).decode('utf-8')
DB_PASSWORD = base64.b64decode(secret.data['db_password']).decode('utf-8')
DB_NAME = base64.b64decode(secret.data['db_name']).decode('utf-8')
DB_HOST = base64.b64decode(secret.data['db_host']).decode('utf-8')
DB_PORT = base64.b64decode(secret.data['db_port']).decode('utf-8')

save_webhook_output_file = "webhooklogs.json"

app = Flask(__name__)

app.config['BASIC_AUTH_USERNAME'] = WEBHOOK_USERNAME
app.config['BASIC_AUTH_PASSWORD'] = WEBHOOK_PASSWORD
app.config['BASIC_AUTH_FORCE'] = True

# Establish database connection
connection = psycopg2.connect(
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME,
    host=DB_HOST,
    port=DB_PORT
)
print("Database connection to {} successful".format(DB_NAME))


basic_auth = BasicAuth(app)

@app.route('/') 
@basic_auth.required
def index():
    return '<h1>Im Alive</h1>', 200

@app.route('/api', methods=['POST'])  
@basic_auth.required
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
    app.run(ssl_context='adhoc', host='0.0.0.0', port=5443, debug=True)
