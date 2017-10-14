import threading
from queue import Queue
import urllib.request
import time
import re
import json
from flask import Flask, render_template
from datetime import datetime

baseUrl = 'https://www.virginactive.co.uk/clubs/'
clubList = ['tower-bridge', 'broadgate', 'canary-riverside', 'bank', 'moorgate', 'walbrook', 'barbican', 'mansion-house', 'aldersgate']
pattern = r'timetableName":"(?P<timetableName>[^"]*)",.*?,"instructor":"(?P<instructor>[^"]*)".*?startTime":"(?P<startTime>\S+?)"'

print_lock = threading.Lock()

clubDictionary = {}
allClasses = []

def get_url(club):
    url = baseUrl + club + "/timetable"
    htmlPage = urllib.request.urlopen(url).read().decode('utf-8')
    regex = re.compile(pattern)
    for match in regex.finditer(htmlPage):
        classes = match.group('timetableName','instructor','startTime')
        clubDictionary.update({"club" : club})
        clubDictionary.update({"timetableName" : classes[0]})
        clubDictionary.update({"instructor" : classes[1]})
        date = datetime.strptime(classes[2],"%Y-%m-%dT%H:%M:%S")
        clubDictionary.update({"date" : date.strftime("%c")})
        allClasses.append(clubDictionary.copy())

    with print_lock:
        print("Downloaded : {}".format(url))

def process_queue():
    while True:
        current_url = url_queue.get()
        get_url(current_url)
        url_queue.task_done()



url_queue = Queue()

for i in clubList:
    t = threading.Thread(target=process_queue)
    t.daemon = True
    t.start()

start = time.time()

for club in clubList:
    url_queue.put(club)

url_queue.join()

print("Downloaded " + str(len(allClasses)) + " classes in {0:.5f}".format(time.time() - start) + " seconds")



app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index2.html', data=allClasses)

@app.route("/api")
def api():
    return json.dumps({"classes" : allClasses})
#    return json.dumps(allClasses)
if __name__ == "__main__":
    app.run('0.0.0.0')
