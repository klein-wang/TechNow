import os
# import gevent.monkey
# import multiprocessing

# gevent.monkey.patch_all()

debug = False
loglevel = 'info'
bind = '0.0.0.0:5002'
# pidfile = 'log/gunicorn.pid'
# logfile = 'log/debug.log'
# certfile = '/app/marsproject/mycert.crt'
# keyfile = '/app/marsproject/mycert.pem'

# 启动的进程数
workers = 4
# workers = multiprocessing.cpu_count()*2+1
threads = 2
worker_class = 'sync'
timeout = 600

