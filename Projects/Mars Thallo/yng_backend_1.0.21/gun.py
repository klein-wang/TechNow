import os
import gevent.monkey
gevent.monkey.patch_all()

import multiprocessing

debug = False
loglevel = 'info'
bind = '0.0.0.0:5000'
# pidfile = 'log/gunicorn.pid'
# logfile = 'log/debug.log'

#启动的进程数
# workers = 4
workers = multiprocessing.cpu_count()*2+1
threads=3
worker_class = 'sync'
timeout = 600


# certfile = '/app/marsproject/mycert.crt'
# keyfile = '/app/marsproject/mycert.pem'
