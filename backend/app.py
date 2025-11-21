from flask import Flask
from flask_cors import CORS
from routes.analyze import analyze_bp
# importing relevant tools

app = Flask(__name__) 
CORS(app) # cross origin rqs

app.register_blueprint(analyze_bp, url_prefix = '/api') # registering blueprints 

@app.route('/health', methods = ['GET'])
def health():
    return {"status": "healthy"}, 200

if __name__ == '__main__':
    app.run(debug = True, host = '0.0.0.0', port = 5000)