from flask import Blueprint, request, jsonify 
import sys 
sys.path.append('..')
# importing blueprint, rq and jsonify and importing from parent folder services

from services.ml_wrapper import predict_defects # importing predicting defects function from the ML wrapper
analyze_bp = Blueprint('analyze', __name__) # blueprint called analyze 

@analyze_bp.route('/analyze', methods = ['POST']) # when someone posts to analyze, run analyze fn 
def analyze():
     # Check if image was uploaded
    if 'image' not in request.files: # if no img, then return error 
        return jsonify({"error": "No image provided"}), 400
           
    image_file = request.files['image'] #grab img
    
    try: 
        # Call ML model
        defects = predict_defects(image_file)
        
        return jsonify({ # if it works basically 
            "success": True,
            "defects": defects
        }), 200
        
    except Exception as e:
        return jsonify({ # will return an error if didnt succeed, try catch  
            "success": False,
            "error": str(e)
        }), 500