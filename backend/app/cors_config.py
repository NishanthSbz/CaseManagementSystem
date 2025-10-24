from flask_cors import CORS

def configure_cors(app):
    # Enable CORS for all routes with specific origins
    CORS(app, 
         resources={
             r"/*": {  # Allow CORS for all routes
                 "origins": [
                     "http://localhost:5173",
                     "http://127.0.0.1:5173",
                     "http://localhost:3000",
                     "http://frontend:5173"
                 ],
                 "methods": ["GET", "HEAD", "POST", "OPTIONS", "PUT", "PATCH", "DELETE"],
                 "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
                 "supports_credentials": True,
                 "expose_headers": ["Content-Range", "X-Total-Count"],
                 "max_age": 600  # Cache preflight requests for 10 minutes
             }
         })