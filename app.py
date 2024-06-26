from flask import Flask, request
from view import view
from edit import edit
from whitelist import whitelist
from atom import atom

app = Flask(__name__,
            static_url_path = "",
            static_folder = "static",
            )
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

app.register_blueprint(view)
app.register_blueprint(edit)
app.register_blueprint(whitelist)
app.register_blueprint(atom)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8123, debug=True)
    print("!", request)
