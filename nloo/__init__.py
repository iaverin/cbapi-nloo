from flask import Flask, request, jsonify, Response
import logging
import json
# import . as nloo
from . import application as nloo
from nloo import core
from logging.config import dictConfig
import sys
import yaml
from nloo import application
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

config = None

def create_app():
    global config

    app = Flask(__name__)

    print("===========")

    # todo: use Flask's native config loading

    try:
        import config

    except ModuleNotFoundError:
        print("config.py not found!", file=sys.stderr)
        print("Rename _config_default.py to config.py", file=sys.stderr)
        exit(0)

    json.ensure_ascii = False

    dictConfig(core.logger_config)
    log = logging.getLogger("application")

    core.init(config, log)

    if not (getattr(config, "REPORTER", False) ):
        print("")
        print("REPORTER settings are not set in config.py. Check _config_default.py for details.", file=sys.stderr)

    core.logger.info("")
    core.logger.info("================ nloo for cb-api launched ==================")

    all_cities = list()
    with open(config.all_cities_file, "r", encoding='utf-8') as f:
        all_cities = f.readlines()

    cities_synonyms = dict()
    with open(config.cities_synonyms, "r", encoding='utf-8') as f:
        cities_synonyms = yaml.load(f, Loader=yaml.BaseLoader)

    print("")

    nloo.init(all_cities, cities_synonyms)

    @app.route('/')
    def hello_world():

        core.log("test_user", "NLOO", "event_test", {"payload": "test"})

        # with app.app_context():
        #     timestamp = datetime.datetime.now(tz=pytz.timezone('UTC'))
        #     event = model.Event(timestamp=timestamp, user_id="test", component="REPORTER",
        #                         event="event_test", payload={"payload": "test"})
        #
        #     db.session.add(event)
        #     db.session.commit()

        return 'NLOO the NLU service'

    @app.route('/city', methods=['GET', 'POST'])
    def city():
        request.get_json(force=False)

        if request.json is not None:
            json_data = request.json
        else:
            json_data = {}

        message = json_data.get("message", None) or request.args.get('message', default=None)
        user_id = json_data.get("userId", None) or request.args.get('userId', default=None)


        detected_city = nloo.detect_city(message, threshold=0)

        if detected_city is not None:
            return json.dumps({"city": detected_city[0],
                               "confidence": detected_city[1] / 100}, ensure_ascii=False)

        return False

    return app


if __name__ == "__main__":
    # execute only if run as a script
    create_app()
