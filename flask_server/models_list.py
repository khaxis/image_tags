#!/usr/bin/env python
from flask_server.common import *
import utils.model_collection as mcoll

@app.route("/models/")
def get_models_list(pool_id=None):
    return render_template('models_list.html', models_list=enumerate(mcoll.getModelsList(pool_id)))


@app.route("/models/<model_id_or_mode>")
def get_model(model_id_or_mode=None):
    if model_id_or_mode == 'filter':
        pool_id = request.args.get('pool_id', None)
        if pool_id:
            return get_models_list(pool_id)
    else:
        model = mcoll.getModel(model_id_or_mode)
        return render_template('model.html', model=model)
