import json
import psycopg2
import requests
import time

if __name__ == '__main__':
    conn = psycopg2.connect(database="jsonb_test", user="root",password="boyu1105" , host="10.14.41.109", port=20158)
    conn.set_session(autocommit=True)
    cur = conn.cursor()

    # The Reddit API wants us to tell it where to start from. The first request
    # we just say "null" to say "from the start"; subsequent requests will use
    # the value received from the last call.
    url = "https://www.reddit.com/r/programming.json"
    after = {"after": "null"}

    for n in range(1):
        # First, make a request to reddit using the appropriate "after" string.
        req = requests.get(url, params=after, headers={"User-Agent": "Python"})
        print(req)

        # Decode the JSON and set "after" for the next request.
        resp = req.json()
        #print(resp)
        after = {"after": str(resp['data']['after'])}

        # Convert the JSON to a string to send to the database.
        data = json.dumps(resp)
        #print(data)

        # The JSON reddit returns looks like this:
        # {
        #   "data": {
        #     "children": [ ... ]
        #   },
        #   "after": ...
        # }
        # We structure our query so that we extract the `children` field, and then
        # expand that and insert each individual element into the database as a
        # separate row.
        #cur.execute("""INSERT INTO jsonb_test.programming (posts)
        #        SELECT json_array_elements(%s->'data'->'children')""", (data,))

        # Reddit limits to 30 requests per minute, so do not do any more than that.
        time.sleep(2)

    cur.close()
    conn.close()

