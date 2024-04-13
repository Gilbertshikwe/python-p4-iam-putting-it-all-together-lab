#!/usr/bin/env python3

from flask import request, session  #type:ignore
from flask_restful import Resource  #type:ignore
from sqlalchemy.exc import IntegrityError #type:ignore

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        image_url = data.get('image_url')
        bio = data.get('bio')

        user = User(
            username=username,
            image_url=image_url,
            bio=bio
        )
        user.password = password

        try:
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
            return {
                'id': user.id,
                'username': user.username,
                'image_url': user.image_url,
                'bio': user.bio
            }, 201
        except IntegrityError as e:
            db.session.rollback()
            errors = {}
            if 'username' in str(e):
                errors['username'] = ['Username is already taken.']
            return {'errors': errors}, 422
        except Exception as e:
            db.session.rollback()
            return {'errors': {'message': 'An error occurred while creating the user.'}}, 422

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            user = User.query.get(user_id)
            return {
                'id': user.id,
                'username': user.username,
                'image_url': user.image_url,
                'bio': user.bio
            }, 200
        else:
            return {'errors': {'message': 'You are not logged in.'}}, 401

class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            return {
                'id': user.id,
                'username': user.username,
                'image_url': user.image_url,
                'bio': user.bio
            }
        else:
            return {'errors': {'message': 'Invalid username or password.'}}, 401

class Logout(Resource):
    def delete(self):
        user_id = session.get('user_id')
        if user_id:
            session.pop('user_id', None)
            return {}, 204
        else:
            return {'errors': {'message': 'You are not logged in.'}}, 401


class RecipeIndex(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            recipes = Recipe.query.filter_by(user_id=user_id).all()
            return [
                {
                    'id': recipe.id,
                    'title': recipe.title,
                    'instructions': recipe.instructions,
                    'minutes_to_complete': recipe.minutes_to_complete,
                    'user': {
                        'id': recipe.user.id,
                        'username': recipe.user.username,
                        'image_url': recipe.user.image_url,
                        'bio': recipe.user.bio
                    }
                } for recipe in recipes
            ], 200
        else:
            return {'errors': {'message': 'You must be logged in to view recipes.'}}, 401

    def post(self):
        user_id = session.get('user_id')
        if user_id:
            data = request.get_json()
            title = data.get('title')
            instructions = data.get('instructions')
            minutes_to_complete = data.get('minutes_to_complete')

            recipe = Recipe(
                title=title,
                instructions=instructions,
                minutes_to_complete=minutes_to_complete,
                user_id=user_id
            )

            try:
                db.session.add(recipe)
                db.session.commit()
                return {
                    'id': recipe.id,
                    'title': recipe.title,
                    'instructions': recipe.instructions,
                    'minutes_to_complete': recipe.minutes_to_complete,
                    'user': {
                        'id': recipe.user.id,
                        'username': recipe.user.username,
                        'image_url': recipe.user.image_url,
                        'bio': recipe.user.bio
                    }
                }, 201
            except IntegrityError as e:
                db.session.rollback()
                errors = {}
                if 'title' in str(e):
                    errors['title'] = ['Title is required.']
                if 'instructions' in str(e):
                    errors['instructions'] = ['Instructions must be at least 50 characters.']
                return {'errors': errors}, 422
        else:
            return {'errors': {'message': 'You must be logged in to create a recipe.'}}, 401

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)