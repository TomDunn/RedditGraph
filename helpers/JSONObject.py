from json import dumps, loads

class JSONObject:

    def __init__(self, **entries):
        self.__dict__.update(entries)

    def json_safe_dict(self):
        return loads(dumps(self.__dict__, skipkeys=True, default=lambda v: None))
