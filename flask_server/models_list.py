#!/usr/bin/env python
from common import *
from model import *
import utils.model_collection as mcoll

@app.route("/models/")
def get_models_list():
	return render_template('models_list.html', models_list=enumerate(pcoll.getModelsList()))
