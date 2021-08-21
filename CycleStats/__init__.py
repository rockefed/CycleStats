from flask import Flask

# using the instance/config.py file instance which isnt committed to git
#app = Flask(__name__)
#app.config.from_object('config')
# Now we can access the configuration variables via app.config["VAR_NAME"].

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')