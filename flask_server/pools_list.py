#!/usr/bin/env python
from common import *
from pool import *
import utils.pool_collection as pcoll

@app.route("/pools/")
def get_pool_list():
	return render_template('pools_list.html', pools_list=enumerate(pcoll.getPoolsList()))
