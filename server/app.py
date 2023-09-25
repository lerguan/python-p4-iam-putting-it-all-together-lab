#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        user_info = request.get_json()
        username = user_info.get('username')
        password = user_info.get('password')
        image_url = user_info.get('image_url')
        bio = user_info.get('bio')

        user = User(
            username=username,
            image_url=image_url,
            bio=bio
        )

        user.password_hash=password

        try:
            db.session.add(user)
            db.session.commit()

            session['user_id'] = user.id
            return user.to_dict(), 201
        except:
            return {'error message': 'Not valid user signup'}, 422


class CheckSession(Resource):
    def get(self):
        user = User.query.filter(User.id==session['user_id']).first()
        if user:
            return user.to_dict(), 200
        else:
            return {'error':'unauthorized user'}, 401

class Login(Resource):
    def post(self):
        username = request.get_json()['username']
        user = User.query.filter(User.username==username).first()
        password = request.get_json()['password']
        if user:

            if user.authenticate(password):
                session['user_id'] = user.id
                return user.to_dict(), 201
        else:
            return {'error':'unauthorized user'}, 401



class Logout(Resource):
    def delete(self):
        user=User.query.filter(User.id==session['user_id']).first()
        if user:
            session['user_id'] = None
            return {}, 204
        return {'error':'Unauthorized'}, 401

class RecipeIndex(Resource):
    def get(self):
        if session.get('user_id'):
            user=User.query.filter(User.id==session['user_id']).first()
            recipe_dict=[recipe.to_dict() for recipe in user.recipes]
            return recipe_dict, 200
        else:
            return {'error':'unauthorized'}, 401
    
    def post(self):
        if session.get('user_id'):
            recipe_json=request.get_json()
            title=recipe_json.get('title')
            instructions=recipe_json.get('instructions')
            minutes_to_complete=recipe_json.get('minutes_to_complete')
            recipe=Recipe(
                    title=title,
                    instructions=instructions,
                    minutes_to_complete=minutes_to_complete,
                    user_id=session['user_id'],
                )
                
            try:
                
                db.session.add(recipe)
                db.session.commit()
                return recipe.to_dict(), 201
            except IntegrityError:
                return {'error':'invalid recipe'}, 422
        return {'error':'unauthorized'}, 401
        
        
api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
