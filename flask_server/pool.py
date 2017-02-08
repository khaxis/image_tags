#!/usr/bin/env python
from common import *
from send_file import *
import utils.pool_collection as pcoll
import utils.model_collection as mcoll
import utils.img_collection as icoll
from utils.common import toObjectID
from collections import defaultdict
import random


SAMPLE_SIZE=10

@app.route("/pools/<pool_id>")
def get_pool(pool_id):
	pool_id = toObjectID(pool_id)
	src_images = pcoll.getSampleOfImages(pool_id)
	class_images = defaultdict(list)
	neg_images = []
	for img in src_images:
		if 'downloadable' not in img or not img['downloadable']:
			continue
		#pos_images.append(img)
		pool_info = [p for p in img['pools'] if p['poolId'] == pool_id][0]
		class_images[pool_info['target']].append(img)

	targets = class_images.keys()
	for k in targets:
		class_images[k] = random.sample(class_images[k], SAMPLE_SIZE)

	models = list(mcoll.getModelsByPoolId(pool_id))

	app.logger.info(models)
	return render_template('pool.html', pool=pcoll.getPool(pool_id)[0], class_images=class_images, models=models)
