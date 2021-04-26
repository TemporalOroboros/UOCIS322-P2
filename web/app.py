"""
Ethan Killen's Flask API.
"""

# Ethan Killen
import config
import logging
import os
from flask import Flask, abort, render_template


logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
log = logging.getLogger(__name__)

HERE = os.path.dirname(__file__)
DOCROOT = HERE

app = Flask(__name__)


# Globals TODO: Make these configurable
FORBIDDEN_PATH_SEGMENTS = ["//", "..", "~"]
ALLOWED_PATH_SUFFIXES = [".html", ".css"]


# Handle requests
@app.route("/<path:request_path>", methods=["GET"])
def handle_request(request_path=None):
	if request_path == None:
		log.info("Recieved file request with no content")
		abort(404)

	if any((segment in request_path) for segment in FORBIDDEN_PATH_SEGMENTS):
		log.info("Rejected file request containing bad segment")
		abort(403)

	if not any(request_path.endswith(suffix) for suffix in ALLOWED_PATH_SUFFIXES):
		log.info("Rejected file request with bad suffix")
		abort(403)

	request_path = os.path.join(DOCROOT, request_path)
	if not os.path.exists(request_path):
		log.info("Rejected nonexistent file request")
		abort(404)

	response_text = None
	with open(request_path, "r") as request_file:
		response_text = request_file.read()

	log.info("Responding to valid file request")
	return response_text, 200



# Handle errors
@app.errorhandler(404)
def page_not_found(exception):
	"""
	Handles a request for a nonexistent page.
	"""
	return render_template("404.html"), 404

@app.errorhandler(403)
def forbidden_page(exception):
	"""
	Handles a request for a forbidden filepath.
	"""
	return render_template("403.html"), 403


def get_options():
	options = config.configuration()
	
	if options.PORT == None:
		log.info("No port configured, defaulting to 5000")
	elif options.PORT <= 1000:
		log.warning("Port {} selected. Ports 0...1000 are reserved by the operating system".format(options.PORT))

	return options


# Booting
if __name__ == "__main__":
	options = get_options()
	
	if options.DEBUG:
		log.setLevel(logging.DEBUG)

	if options.DOCROOT:
		DOCROOT = os.path.join(HERE, options.DOCROOT)
	
	app.run(debug=True, host='0.0.0.0', port=options.PORT)

