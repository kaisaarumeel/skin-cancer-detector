# Contributors:
# * Contributor: <arvinra@student.chalmers.se>
# * Contributor: <elindstr@student.chalmers.se>
# * Contributor: <kaisa.arumeel@gmail.com>
import time
import threading
from queue import Queue
from .job import Job

# Global queue to store prediction jobs
# Using the built in Queue class ensures thread safety
# Docs: https://docs.python.org/3/library/queue.html#queue.Queue
PREDICTION_JOBS = Queue()
MGR_INIT = False
