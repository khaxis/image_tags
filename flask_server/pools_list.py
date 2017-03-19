#!/usr/bin/env python
from flask_server.common import *
from flask_server.pool import *
import utils.pool_collection as pcoll

@app.route("/pools/")
def get_pool_list():
    return render_template('pools_list.html', pools_list=enumerate(pcoll.getPoolsList()))
