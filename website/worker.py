# RedisLabs Worker
# from redis import Redis
# from rq import Queue, Connection
# from rq.worker import HerokuWorker as Worker

# listen = ['high', 'default', 'low']

# url_redis = "redis-13020.c98.us-east-1-4.ec2.cloud.redislabs.com"
# port_redis = "13020"
# db_redis = 'restoku'
# password_redis = '1U8h7PCGI7zLxfme55d493sdcWC0ioGo'
# conn_redis = Redis(host=url_redis, port=port_redis, db=0, password=password_redis)


# if __name__ == '__main__':
#     with Connection(conn_redis):
#         worker = Worker(map(Queue, listen))
#         worker.work(with_scheduler=True)

# Redis Localhost
from redis import Redis
from rq import Queue, Connection, Worker

listen = ['high', 'default', 'low']

# RedisLabs URL Connection
# url_redis = "redis-13020.c98.us-east-1-4.ec2.cloud.redislabs.com"
# port_redis = "13020"
# db_redis = 'restoku'
# password_redis = '1U8h7PCGI7zLxfme55d493sdcWC0ioGo'
# conn_redis = Redis(host=url_redis, port=port_redis, db=0, password=password_redis)

conn_redis = Redis()

if __name__ == '__main__':
    with Connection(conn_redis):
        worker = Worker(map(Queue, listen))
        worker.work(with_scheduler=True)