#!/usr/bin/env python
from common import *
import utils.model_collection as pcoll

@app.route("/models/<model_id>")
def get_model(model_id):
	return render_template('model.html', model=pcoll.getModel(model_id)[0])
