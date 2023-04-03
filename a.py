import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('54.158.113.41', 5672, '/', pika.PlainCredentials('user', 'password')))
channel = connection.channel()
channel.basic_publish(exchange='my_exchange', routing_key='test', body='Hola mundo!')
print("Running produccer App...")
print("[x] Sent 'Hello World...!'")
connection.close()
