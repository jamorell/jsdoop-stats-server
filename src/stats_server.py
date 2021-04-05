import mysql.connector
from flask import Flask, abort, jsonify
from flask_mysqlpool import MySQLPool
from flask import request
from flask_cors import CORS, cross_origin
import json
import signal
from threading import Thread

STATS_SERVER_PORT = 8082
#RABBIT_HOST = "localhost" 
#RABBIT_PORT = 5672
RABBIT_PREFETCH_COUNT = 32
RABBIT_TEST_RESULT_QUEUE = "test_result"
RABBIT_STATS_QUEUE = "stats"

#https://pypi.org/project/flask-mysqlpool/
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

app.config['MYSQL_HOST'] = 'db' #'localhost'
#app.config['MYSQL_PORT'] = 61111
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASS'] = 'password'
app.config['MYSQL_DB'] = 'jsdoop'
app.config['MYSQL_POOL_NAME'] = 'mysql_pool'
app.config['MYSQL_POOL_SIZE'] = 10
app.config['MYSQL_AUTOCOMMIT'] = True
app.config['MYSQL_AUTH_PLUGIN'] = 'mysql_native_password'

db = MySQLPool(app)


@app.route('/user_stats')
@cross_origin()
def get_user_stats():
  try:
    id_job = int(request.args.get('id_job'))
    conn = db.connection.get_connection()  # get connection from pool  
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT username, count(*) as gradients FROM  (select * from stats where idJob = ' + str(id_job) + ' and typeTask like "save_gradients") A group by username order by gradients DESC', )
    result = cursor.fetchall()
    conn.close()  # return connection to pool
  except err:
    print(err)
    abort(500)  
  to_json = [dict(row) for row in result]
  return jsonify(to_json)
  






def acc_cb(ch, method, properties, body):
  # Read the string representing json
  # Into a python list of dicts.
  with app.app_context():
    conn = db.connection.get_connection()  # get connection from pool  
    print("received acc body = " + str(body))
    myjson = json.loads(body)
    print("received " + str(myjson["requestTime"]) + " " + str(myjson["ageModel"]) + " " + str(myjson["loss"]))
    mycursor = conn.cursor()
    sql = "INSERT IGNORE INTO test_acc_loss(idJob, ageModel, confusion_matrix, loss, acc, requestTime, responseTime) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    print("confusion_matrix = " + str(myjson["confusion_matrix"]) )
    values = (myjson["idJob"], myjson["ageModel"], str(myjson["confusion_matrix"]), myjson["loss"], myjson["acc"], myjson["requestTime"], myjson["responseTime"])
    mycursor.execute(sql, values)
    conn.commit()
    print("ACK " + str(method.delivery_tag))
    channel.basic_ack(method.delivery_tag)
    conn.close()  # return connection to pool







total_to_sql = 10
list_values = []
to_ack = []
def stats_cb(ch, method, properties, body):
  # Read the string representing json
  # Into a python list of dicts.
  with app.app_context():
    conn = db.connection.get_connection()  # get connection from pool  
    myjson = json.loads(body)
    print("received stats body = " + str(body))
    print("received " + str(myjson["timeRequest"]) + " " + str(myjson["typeTask"]))
    mycursor = conn.cursor()
    sql = "INSERT IGNORE INTO stats(infoWorker, remoteAddr, timeRequest, timeResponse, ageModel, idJob, typeTask, other, username, idTask, executionTime) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    values = (myjson["infoWorker"], myjson["remoteAddr"], myjson["timeRequest"], myjson["timeResponse"], myjson["ageModel"], myjson["idJob"], myjson["typeTask"], myjson["other"], myjson["username"], myjson["idTask"], myjson["executionTime"])
    list_values.append(values)
    to_ack.append(method.delivery_tag)
    if (len(list_values) >= total_to_sql):  
      #mycursor.execute(sql, values)
      mycursor.executemany(sql, list_values)
      conn.commit()
      list_values.clear()
      for i in range(len(to_ack)):
        print("ACK " + str(to_ack[i]))
        channel.basic_ack(to_ack[i])
        #print("ACK " + str(method.delivery_tag))
        #channel.basic_ack(method.delivery_tag)
      to_ack.clear()

    conn.close()  # return connection to pool





import pika

#connection = pika.BlockingConnection(pika.ConnectionParameters(host = RABBIT_HOST, port = RABBIT_PORT))
connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))

channel = connection.channel()
channel.basic_qos(prefetch_count=(RABBIT_PREFETCH_COUNT)) 



#3- Subscribe to Results Queue
channel.queue_declare(queue=RABBIT_TEST_RESULT_QUEUE, durable=False)
channel.queue_declare(queue=RABBIT_STATS_QUEUE, durable=True)

channel.basic_consume(queue=RABBIT_TEST_RESULT_QUEUE,
                      auto_ack=False,
                      consumer_tag="a-consumer-tag",  
                      on_message_callback=acc_cb)

channel.basic_consume(queue=RABBIT_STATS_QUEUE,
                      auto_ack=False,
                      consumer_tag="a-consumer-tag2",  
                      on_message_callback=stats_cb)



def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    db.close()
    channel.close()
    connection.close()    
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
print(' [*] Waiting for messages. To exit press CTRL+C')

#channel.start_consuming()
#app.run(host='0.0.0.0', port=STATS_SERVER_PORT)

thread1 = Thread(target = channel.start_consuming) #Thread(target = channel.start_consuming())
thread1.start()

thread2 = Thread(target = app.run, args = ['0.0.0.0', STATS_SERVER_PORT]) #args = ['0.0.0.0', STATS_SERVER_PORT]) #Thread(target = app.run(host='0.0.0.0', port=STATS_SERVER_PORT))
thread2.start()

