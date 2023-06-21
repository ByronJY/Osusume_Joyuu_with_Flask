import os

from library.db_ctl import db_init
from library.routing_user import app


if __name__ == '__main__':
    db_init()
    app.debug = True
    host = os.environ.get('IP', '0.0.0.0')
    port = int(os.environ.get('PORT', 8080))
    app.run(host=host, port=port)
