import datetime

from flask import Flask
from flask.json.provider import DefaultJSONProvider

class UpdatedJSONProvider(DefaultJSONProvider):
    def default(self, o):
        if isinstance(o, datetime.timedelta):
            return "{:02d}:{:02d}".format(o.seconds//3600, (o.seconds//60) % 60)
        return super().default(o)