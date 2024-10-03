import os
import boto3
import io
from PIL import Image
from flask import Flask, request, jsonify
import logging
from dotenv import load_dotenv

app = Flask(__name__)

# Cargar el archivo .env
load_dotenv()

rekognition = boto3.client('rekognition', 
                           region_name='us-east-1',
                           aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                           aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))

dynamodb = boto3.client('dynamodb', 
                        region_name='us-east-1',
                        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))

logging.basicConfig(level=logging.INFO)

@app.route('/login', methods=['POST'])
def login():
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400

    image_file = request.files['image']
    try:
        image = Image.open(image_file.stream)
        stream = io.BytesIO()
        image.save(stream, format="JPEG")
        image_binary = stream.getvalue()
    except Exception as e:
        logging.error(f"Error processing image: {str(e)}")
        return jsonify({"error": "Error processing image"}), 500

    try:
        face_detection = rekognition.detect_faces(
            Image={'Bytes': image_binary},
            Attributes=['ALL']
        )

        if not face_detection['FaceDetails']:
            return jsonify({"error": "No faces detected in the image"}), 400
    except Exception as e:
        logging.error(f"Error detecting faces: {str(e)}")
        return jsonify({"error": f"Error detecting faces: {str(e)}"}), 500

    try:
        response = rekognition.search_faces_by_image(
            CollectionId='jarvistec',
            Image={'Bytes': image_binary}
        )

        found = False
        person_name = None

        for match in response.get('FaceMatches', []):
            face_id = match['Face']['FaceId']
            face = dynamodb.get_item(
                TableName='face_recognition',
                Key={'RekognitionId': {'S': face_id}}
            )

            if 'Item' in face:
                person_name = face['Item']['FullName']['S']
                found = True
                break

        if found:
            return jsonify({"found":True,"message": "Persona encontrada", "name": person_name}), 200
        else:
            return jsonify({"found":False,"message": "Persona no registrada."}), 200
    except Exception as e:
        logging.error(f"Error searching face: {str(e)}")
        return jsonify({"error": f"Error searching face: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
