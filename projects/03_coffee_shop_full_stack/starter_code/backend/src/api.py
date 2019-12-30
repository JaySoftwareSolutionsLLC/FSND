import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS, cross_origin

from .database.models import db, db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@ DONE uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

## ROUTES
'''
@DONE implement endpoint
    GET /drinks
        DONE it should be a public endpoint
        DONE it should contain only the drink.short() data representation
        DONE returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        DONE? or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
@cross_origin()
def retrieve_drinks():
    body = {}
    try:
        drinks = Drink.query.all()
        short_drinks = []
        for d in drinks:
            short_drinks.append(d.short())
        body['success'] = True
        # body['len'] = len(drinks)
        body['drinks'] = short_drinks
    except:
        body['success'] = False
    finally:
        return jsonify(body)


'''
@DONE implement endpoint
    GET /drinks-detail
        DONE it should require the 'get:drinks-detail' permission
        DONE it should contain the drink.long() data representation
        DONE returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        DONE? or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@cross_origin()
@requires_auth('get:drinks-detail')
# requires get:drinks-detail permission
def retrieve_drinks_detail(jwt):
    body = {}
    drinks = Drink.query.all()
    long_drinks = []
    for d in drinks:
        long_drinks.append(d.long())
        # Issue is being caused because posted items use single quotes in recipe string rather than double quotes
    body['success'] = True
    body['drinks'] = long_drinks
    return jsonify(body)

'''
@DONE implement endpoint
    POST /drinks
        DONE it should create a new row in the drinks table
        DONE it should require the 'post:drinks' permission
        DONE it should contain the drink.long() data representation
        DONE returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        DONE? or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@cross_origin()
@requires_auth('post:drinks')
def post_drink(jwt):
    body = {}
    try:
        title = request.json['title']
        # recipe = str([{"color": "sienna", "name":"Angel's Envy Rye", "parts":5}, {"color": "peru", "name":"Sweet Vermouth", "parts":1}])
        recipe = json.dumps(request.json['recipe'])
        new_drink = Drink(title = title, recipe = recipe)
        db.session.add(new_drink)
        db.session.commit()
        body['success'] = True
        body['drinks'] = new_drink.long()
    except:
        body['success'] = False
    finally:
        return jsonify(body)


'''
@DONE implement endpoint
    PATCH /drinks/<id>
        DONE where <id> is the existing model id
        DONE it should respond with a 404 error if <id> is not found
        DONE it should update the corresponding row for <id>
        DONE it should require the 'patch:drinks' permission
        DONE it should contain the drink.long() data representation
        DONE returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        DONE? appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@cross_origin()
@requires_auth('patch:drinks')
def patch_drink(jwt, id):
    req = request.get_json()
    body = {}
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if drink is None:
        abort(404)
    else:
        try:
            # for attr, value in req.items():
                # drink.attr = value
            if 'title' in req:
                drink.title = str(req.get('title'))
            if 'recipe' in req:
                drink.recipe = json.dumps(req.get('recipe'))
            drink.update()
                # drink.commit()
            body['success'] = True
            body['drinks'] = [drink.long()]
        except:
            body['success'] = False
        finally:
            return jsonify(body)

'''
@DONE implement endpoint
    DELETE /drinks/<id>
        DONE where <id> is the existing model id
        DONE it should respond with a 404 error if <id> is not found
        DONE it should delete the corresponding row for <id>
        DONE it should require the 'delete:drinks' permission
        DONE returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        DONE? or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@cross_origin()
@requires_auth('delete:drinks')
def delete_drink(jwt, id):
    body = {}
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if drink is None:
        abort(404)
    else:
        try:
            drink.delete()
            db.session.commit()
            body['success'] = True
            body['delete'] = drink.id
        except:
            body['success'] = False
        finally:
            return jsonify(body)

## Error Handling
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
@DONE implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@DONE implement error handler for 404
    error handler should conform to general task above 
'''


'''
@DONE implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(AuthError)
def handle_auth_error(ex):
    print(jsonify(ex.error))
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response