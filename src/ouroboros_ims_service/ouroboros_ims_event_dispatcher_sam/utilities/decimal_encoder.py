import decimal
import json


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            # wanted a simple yield str(o) in the next line,
            # but that would mean a yield on the line with super(...),
            # which wouldn't work (see my comment below), so...
            if str(o) == str(int(o)):
                return int(o)
            else:
                return float(o)
        return super(DecimalEncoder, self).default(o)