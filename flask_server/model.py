#!/usr/bin/env python
from common import *
import utils.model_collection as mcoll

@app.route("/models/<model_id>")
def get_model(model_id):
	model = mcoll.getModel(model_id)
	return render_template('model.html', model=model)
