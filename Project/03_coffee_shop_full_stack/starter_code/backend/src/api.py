import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from jose import jwt
from functools import wraps
from urllib.request import urlopen
from .database.models import db_drop_and_create_all, setup_db, Drink, db
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

AUTH0_DOMAIN = 'dev-m63c4eg2y8coipcr.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'https://localhost:5000'

'''
@DONE uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@DONE implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=["GET"])
@requires_auth('get:drinks')
def get_drinks(jwt):
    drinks = Drink.query.all()
    drinksFormmatted = [drink.short() for drink in drinks]

    return jsonify({
        'success': True,
        'drinks': drinksFormmatted
    })

'''
@DONE implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=["GET"])
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    drinks = Drink.query.all()
    drinksFormmatted = [drink.long() for drink in drinks]

    return jsonify({
        'success': True,
        'drinks': drinksFormmatted
    })

'''
@DONE implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=["POST"])
@requires_auth('post:drinks')
def post_drinks(jwt):
    data = request.get_json()
    title = data.get('title', None)
    recipe = data.get('recipe', None)

    if not title or not recipe:
        abort(400)

    newDrink = Drink()
    newDrink.title = title
    newDrink.recipe = json.dumps(recipe)

    try:
        newDrink.insert()
    except Exception as e:
        db.session.rollback()
        print(e)
        abort(500)

    return jsonify({
        'success': True,
        'drinks': [newDrink.long()]
    })


'''
@DONE implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=["PATCH"])
@requires_auth('patch:drinks')
def patch_drinks(jwt, drink_id):
    data = request.get_json()
    drink = Drink.query.get(drink_id)
    title = data.get('title', None)
    recipe = data.get('recipe', None)

    if (not title and not recipe) or not drink:
        abort(400)

    if title:
        drink.title = title
    if recipe:
        drink.recipe = json.dumps(recipe)

    try:
        drink.update()
    except:
        db.session.rollback()
        abort(500)

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    })


'''
@DONE implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=["DELETE"])
@requires_auth('delete:drinks')
def delete_drink(jwt, drink_id):
    drink = Drink.query.get(drink_id)

    if not drink:
        abort(400)

    try:
        drink.delete()
    except:
        db.session.rollback()
        abort(500)
    finally:
        db.session.close()
    
    return jsonify({
        'success': True,
        'delete': drink_id
    })


# Error Handling
'''
Example error handling for unprocessable entity
'''

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

'''
@DONE implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "not found"
    }), 404

'''
@DONE implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": error.error,
        "message": "error.error"
    }), error.status_code