#!/usr/bin/env python
from common import *
from pools_list import *
from models_list import *


@app.route("/")
@app.route("/index")
def main():
	return render_template('index.html')


if __name__ == "__main__":
	urls_for()
	app.run()
