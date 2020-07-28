#! /usr/bin/env python3

# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from datetime import datetime
from datetime import timedelta
from dateutil import parser
import itertools
import json
import pytz
import subprocess
import time
import requests

import cgi, cgitb
cgitb.enable()

print("Content-Type: text/html\n")


ROUTE_NAMES = {
    "747": "CT2"
}


class Prediction(object):
    def __init__(self, route, departs):
        self.route = ROUTE_NAMES.get(route, route)
        self.departs = parser.parse(departs)

    def routeclass(self):
        return "route-" + self.route
        
    def time_in_future(self):
        return self.departs - datetime.now(pytz.utc).replace(microsecond=0)

    def minutes(self):
        return int(self.time_in_future().total_seconds() / 60)
    
    def ignore(self):
        future = self.time_in_future()
        return future > timedelta(hours=4) or future < timedelta()
    
    def html(self):
        return """<div class="pred {routeclass}">
<div class="route">{route}</div>
<div class="departs">{departs} min</div>
</div>""".format(route=self.route,
                 routeclass=self.routeclass(),
                 departs=str(self.minutes()))
#                 departs=str(self.time_in_future())[:-3])


def get_stop(stop):
    pred_list = []
    try:
        response = requests.get("https://api-v3.mbta.com/predictions?filter[stop]={}&sort=departure_time".format(stop))
    except requests.HTTPError as e:
        return ["Got %d" % e.code]
    except requests.URLError as e:
        return ["URLError %s" % e.reason]

    if response.status_code != 200:
        return ["Got %d" % response.code]

    returned = response.json()
    for pred in returned["data"]:
        departs = pred["attributes"]["departure_time"]
        if not departs:
            continue
        p = Prediction(route=pred["relationships"]["route"]["data"]["id"],
                       departs=departs)
        if not p.ignore():
            pred_list.append(p)
    return pred_list


def from_sullivan():
    return get_stop(2757)
def to_sullivan():
    return get_stop(2779)


def get_predictions():
    table = []
    def html(s):
        if type(s) == str:
            return s
        return s.html()
    
    empty = True
    for from_pred, to_pred in itertools.zip_longest(from_sullivan(), to_sullivan(), fillvalue=""):
        empty = False
        table.append("<tr><td>{from_pred}</td><td>{to_pred}</td></tr>".format(
            from_pred=html(from_pred),
            to_pred=html(to_pred)))
    if not empty:
        subprocess.Popen(["/bin/bash", "/home/pi/bin/turn-on-screen"]).communicate()

    with open("predictions.template.html") as pred_tmpl:
        return pred_tmpl.read().format(predictions="\n".join(table))


def orange_line():
    preds = get_stop(70030)
    mins = []
    for pred in preds[:2]:
        if type(pred) == str:
            mins.append(pred)
        else:
            m = pred.minutes()
            mins.append("{} min{}".format(m, "" if m == 1 else "s"))
    inbound = "<div class=\"inbound\"><div class=\"label\">Orange Inbound:</div>\n{}</div>".format("<br>\n".join(mins))
    preds = get_stop(70031)
    mins = []
    for pred in preds[:2]:
        if type(pred) == str:
            mins.append(pred)
        else:
            m = pred.minutes()
            mins.append("{} min{}".format(m, "" if m == 1 else "s"))
    outbound = "<div><div class=\"label\">Orange Outbound:</div>\n{}</div>".format("<br>\n".join(mins))
    return outbound + inbound


def get_metadata():
    return """<div class="orangeline">{}</div><div class="time">{}</div>""".format(
        orange_line(),
        time.strftime("%m/%d<br>%A,<br>%I:%M %p"))


predictions = get_predictions()

with open("index.template.html") as index_html:
    print(index_html.read().format(metadata=get_metadata(), predictions=predictions))

# https://api-v3.mbta.com/predictions?filter[stop]=12759
