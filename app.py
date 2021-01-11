from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restplus import Api, fields, Resource
from cfenv import AppEnv
import os

app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@192.168.146.128:5432/test'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///testDatabase.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
env = AppEnv()
pgservice = env.get_service(label='a9s-postgresql11')
app.config['SQLALCHEMY_DATABASE_URI'] = pgservice.credentials['uri']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api()
api.init_app(app)




#Table
class users(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    email = db.Column(db.String)
    password = db.Column(db.String)

db.create_all()

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id','username','email','password')


model = api.model('model',{
    'username':fields.String('Enter username'),
    'email':fields.String('Enter email'),
    'password':fields.String('Enter password')
})

user_schema = UserSchema()
users_schema = UserSchema(many=True)

@api.route('/getdata')
class Getdate(Resource):
    def get(self):
        data = users.query.all()
        return jsonify(users_schema.dumps(data))

@api.route('/postdata')
class postdate(Resource):
    @api.expect(model)
    def post(self):
        user = users(username=request.json['username'], email=request.json['email'], password=request.json['password'])
        db.session.add(user)
        db.session.commit()
        return {'message': 'data added to the database'}

@api.route('/putdata/<int:id>')
class putdata(Resource):
    @api.expect(model)
    def put(self, id):
        user = users.query.get(id)
        user.username = request.json['username']
        user.email =request.json['email']
        user.password = request.json['password']
        db.session.commit()
        return {'message': 'data updated'}

@api.route('/deletedata/<int:id>')
class deletedata(Resource):
    def delete(self,id):
        user = users.query.get(id)
        db.session.delete(user)
        db.session.commit()
        return {'message': 'data deleted successfully'}





port = int(os.getenv("PORT"))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)


