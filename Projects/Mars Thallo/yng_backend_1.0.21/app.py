
from marsproject import create_app
from flask_cors import CORS

app = create_app()
CORS(app, supports_credentials=True)  # 解决跨域问题

if __name__ == '__main__':
    app.config['JSON_AS_ASCII'] = False
    app.run(host='0.0.0.0',port=5000,debug=False)
