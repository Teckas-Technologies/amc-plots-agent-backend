from flask import Flask, request, jsonify
from flask_cors import CORS
from service import chat_service

import os
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') # load SECRET_KEY using .env file
CORS(app)


# POST api to post a query and get a chat response
# Body - prompt contains user's query
# return streamed response to the front-end
@app.route("/voice-backend", methods=[ 'POST'])
def voiceAssistant():
    try:
        data = request.get_json()
        query = data.get('prompt')

        user_id = data.get('id')

        print(query, user_id)

        # def generate():
        #     # response = chat_service.retrieval_from_doc(query=query)
        #     # for token in response:
        #     #     # print(token)
        #     #     yield token

        data = chat_service.retrieval_from_doc(str(user_id), str(query))

        return jsonify({"status": 200, "data": data, "success":True})
    except Exception as e:
        print("Error :", e)
        return jsonify({"status": 500, "data": str(e), "success": False})
    


@app.route("/clear-history", methods=[ 'POST'])
def clearHistory():
    try:
        req = request.get_json()

        user_id = req.get('id')

        print( user_id)

        data = chat_service.clear_history_from_buffer(str(user_id))

        return jsonify({"status": 200, "data": data, "success":True})
    except Exception as e:
        print("Error :", e)
        return jsonify({"status": 500, "data": str(e), "success": False})
    

if __name__ == '__main__':
    app.run(debug=True)