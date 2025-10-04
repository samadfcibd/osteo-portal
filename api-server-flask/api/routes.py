# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from datetime import datetime, timezone, timedelta

from functools import wraps

from flask import request
from flask_restx import Api, Resource, fields, Namespace

import jwt

from .model import *
from .config import BaseConfig
import requests
from sqlalchemy import func, distinct, case, text
from bs4 import BeautifulSoup
import pandas as pd
import os
from flask import request, current_app
from werkzeug.utils import secure_filename
from flask import send_from_directory, make_response


rest_api = Api(version="1.0", title="Users API")


"""
    Flask-Restx models for api request and response data
"""

signup_model = rest_api.model('SignUpModel', {"username": fields.String(required=True, min_length=2, max_length=32),
                                              "email": fields.String(required=True, min_length=4, max_length=64),
                                              "password": fields.String(required=True, min_length=4, max_length=16)
                                              })

login_model = rest_api.model('LoginModel', {"email": fields.String(required=True, min_length=4, max_length=64),
                                            "password": fields.String(required=True, min_length=4, max_length=16)
                                            })

user_edit_model = rest_api.model('UserEditModel', {"userID": fields.String(required=True, min_length=1, max_length=32),
                                                   "username": fields.String(required=True, min_length=2, max_length=32),
                                                   "email": fields.String(required=True, min_length=4, max_length=64)
                                                   })
                                                
organism_list_model = rest_api.model('OrganismListModel', {
    "stage": fields.Integer(required=True, description="Stage ID")
})


"""
   Helper function for JWT token required
"""

# def token_required(f):

#     @wraps(f)
#     def decorator(*args, **kwargs):

#         token = request.headers["authorization"]
#         if not token:
#             return {"success": False, "msg": "Valid JWT token is missing"}, 400

#         try:
#             # return {"success": False, "msg": BaseConfig.SECRET_KEY}, 400
#             data = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=["HS256"])
#             current_user = Users.get_by_email(data["email"])

#             if not current_user:
#                 return {"success": False,
#                         "msg": "Sorry. Wrong auth token. This user does not exist."}, 400

#             token_expired = db.session.query(JWTTokenBlocklist.id).filter_by(jwt_token=token).scalar()

#             if token_expired is not None:
#                 return {"success": False, "msg": "Token revoked."}, 400

#             if not current_user.check_jwt_auth_active():
#                 return {"success": False, "msg": "Token expired."}, 400

#         except jwt.ExpiredSignatureError:
#             return {"success": False, "msg": "Token expired"}, 401  # Specific HTTP 401
#         except Exception as e:
#             return {"success": False, "msg": str(e)}, 400

#         return f(current_user, *args, **kwargs)

#     return decorator


def token_required(f):

    @wraps(f)
    def decorator(*args, **kwargs):

        token = request.headers["authorization"]
        if not token:
            return {"success": False, "msg": "Valid JWT token is missing"}, 400

        try:
            data = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=["HS256"])
            current_user = Users.get_by_email(data["email"])

            if not current_user:
                return {"success": False,
                        "msg": "Sorry. Wrong auth token. This user does not exist."}, 400

            token_expired = db.session.query(JWTTokenBlocklist.id).filter_by(jwt_token=token).scalar()

            if token_expired is not None:
                return {"success": False, "msg": "Token revoked."}, 400

            if not current_user.check_jwt_auth_active():
                return {"success": False, "msg": "Token expired."}, 400
        except jwt.ExpiredSignatureError:
            return {"success": False, "msg": "Token expired"}, 401  # Specific HTTP 401
        except:
            return {"success": False, "msg": "Token is invalid"}, 400

        return f(current_user, *args, **kwargs)

    return decorator


"""
    Flask-Restx routes
"""


# @rest_api.route('/api/users/register')
# class Register(Resource):
#     """
#        Creates a new user by taking 'signup_model' input
#     """

#     @rest_api.expect(signup_model, validate=True)
#     def post(self):
#         print('asdfsd')

#         req_data = request.get_json()

#         _username = req_data.get("username")
#         _email = req_data.get("email")
#         _password = req_data.get("password")

#         user_exists = Users.get_by_email(_email)
#         if user_exists:
#             return {"success": False,
#                     "msg": "Email already taken"}, 400

#         new_user = Users(username=_username, email=_email)

#         new_user.set_password(_password)
#         new_user.save()

#         return {"success": True,
#                 "userID": new_user.id,
#                 "msg": "The user was successfully registered"}, 200


# @rest_api.route('/api/users/login')
# class Login(Resource):
#     """
#        Login user by taking 'login_model' input and return JWT token
#     """

#     @rest_api.expect(login_model, validate=True)
#     def post(self):

#         req_data = request.get_json()

#         _email = req_data.get("email")
#         _password = req_data.get("password")

#         user_exists = Users.get_by_email(_email)

#         if not user_exists:
#             return {"success": False,
#                     "msg": "This email does not exist."}, 400

#         if not user_exists.check_password(_password):
#             return {"success": False,
#                     "msg": "Wrong credentials."}, 400

#         # create access token uwing JWT
#         token = jwt.encode({'email': _email, 'exp': datetime.utcnow() + timedelta(minutes=30)}, BaseConfig.SECRET_KEY)

#         user_exists.set_jwt_auth_active(True)
#         user_exists.save()

#         return {"success": True,
#                 "token": token,
#                 "user": user_exists.toJSON()}, 200


@rest_api.route('/api/users/edit')
class EditUser(Resource):
    """
       Edits User's username or password or both using 'user_edit_model' input
    """

    @rest_api.expect(user_edit_model)
    @token_required
    def post(self, current_user):

        req_data = request.get_json()

        _new_username = req_data.get("username")
        _new_email = req_data.get("email")

        if _new_username:
            self.update_username(_new_username)

        if _new_email:
            self.update_email(_new_email)

        self.save()

        return {"success": True}, 200


# @rest_api.route('/api/users/logout')
# class LogoutUser(Resource):
#     """
#        Logs out User using 'logout_model' input
#     """

#     @token_required
#     def post(self, current_user):

#         token = request.headers.get("authorization")
#         if not token:
#             return {"success": False, "msg": "Token missing"}, 400

#         try:
#             # Attempt to decode (but don't fail if expired)
#             try:
#                 jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=["HS256"])
#             except jwt.ExpiredSignatureError:
#                 pass  # Still allow revoking expired tokens

#             # Add token to blocklist
#             jwt_block = JWTTokenBlocklist(
#                 jwt_token=token,
#                 created_at=datetime.now(timezone.utc)
#             )
#             db.session.add(jwt_block)
#             db.session.commit()

#             return {"success": True}, 200
#         except Exception as e:
#             return {"success": False, "msg": str(e)}, 400
    
# @rest_api.route('/api/users/logout')
# class LogoutUser(Resource):
#     """
#        Logs out User using 'logout_model' input
#     """

#     @token_required
#     def post(self, current_user):

#         _jwt_token = request.headers["authorization"]

#         jwt_block = JWTTokenBlocklist(jwt_token=_jwt_token, created_at=datetime.now(timezone.utc))
#         jwt_block.save()

#         self.set_jwt_auth_active(False)
#         self.save()

#         return {"success": True}, 200


@rest_api.route('/api/sessions/oauth/github/')
class GitHubLogin(Resource):
    def get(self):
        code = request.args.get('code')
        client_id = BaseConfig.GITHUB_CLIENT_ID
        client_secret = BaseConfig.GITHUB_CLIENT_SECRET
        root_url = 'https://github.com/login/oauth/access_token'

        params = { 'client_id': client_id, 'client_secret': client_secret, 'code': code }

        data = requests.post(root_url, params=params, headers={
            'Content-Type': 'application/x-www-form-urlencoded',
        })

        response = data._content.decode('utf-8')
        access_token = response.split('&')[0].split('=')[1]

        user_data = requests.get('https://api.github.com/user', headers={
            "Authorization": "Bearer " + access_token
        }).json()
        
        user_exists = Users.get_by_username(user_data['login'])
        if user_exists:
            user = user_exists
        else:
            try:
                user = Users(username=user_data['login'], email=user_data['email'])
                user.save()
            except:
                user = Users(username=user_data['login'])
                user.save()
        
        user_json = user.toJSON()

        token = jwt.encode({"username": user_json['username'], 'exp': datetime.utcnow() + timedelta(minutes=30)}, BaseConfig.SECRET_KEY)
        user.set_jwt_auth_active(True)
        user.save()

        return {"success": True,
                "user": {
                    "_id": user_json['_id'],
                    "email": user_json['email'],
                    "username": user_json['username'],
                    "token": token,
                }}, 200
    

# @rest_api.route('/api/clinical-stages')
# class ClinicalStages(Resource):
#     def get(self):
#         try:
#             results = ClinicalStage.query.all()
            
#             # Convert results to a list of dictionaries
#             results = [{'stage_id': stage.stage_id, 'stage_name': stage.stage_name} for stage in results] 

#             # Add the "Select stage" option at the beginning
#             select_option = {
#                 'stage_id': '',
#                 'stage_name': 'Select stage'
#             }
#             results.insert(0, select_option)
            
#             # Return JSON response
#             return {
#                 'success': True,
#                 'data': results
#             }
#         except Exception as e:
#             return {
#                 'success': False,
#                 'message': str(e)
#             }
        
@rest_api.route('/api/proteins')
class Proteins(Resource):
    def get(self):
        try:
            results = Protein.query.all()
            
            # Convert results to a list of dictionaries
            results = [{'protein_id': protein.protein_id, 'protein_name': protein.protein_name} for protein in results] 

            # Add the "Select stage" option at the beginning
            select_option = {
                'protein_id': '',
                'protein_name': 'Select protein'
            }
            results.insert(0, select_option)
            
            # Return JSON response
            return {
                'success': True,
                'data': results
            }
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }
        

@rest_api.route('/api/compounds')
class Compounds(Resource):
    def get(self):
        try:
            # Get only unique compounds based on compound_name
            results = Compound.query.distinct(Compound.compound_name).all()
            
            # Convert results to a list of dictionaries
            compounds_list = [{'compound_id': compound.compound_id, 'compound_name': compound.compound_name} for compound in results] 

            # Add the "Select compound" option at the beginning
            select_option = {
                'compound_id': '',
                'compound_name': 'Select compound'
            }
            compounds_list.insert(0, select_option)
            
            # Return JSON response
            return {
                'success': True,
                'data': compounds_list
            }
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }

@rest_api.route("/api/organisms")
class Organisms(Resource):
    @rest_api.doc(params={
        'stage': {'description': 'Stage ID', 'in': 'query', 'type': 'integer', 'required': True},
        'page': {'description': 'Page number for pagination', 'in': 'query', 'type': 'integer', 'required': False, 'default': 1},
        'per_page': {'description': 'Number of items per page', 'in': 'query', 'type': 'integer', 'required': False, 'default': 10}
    })

    # @rest_api.expect(organism_list_model)
    def get(self):
        try:
            stage = request.args.get("stage")
            
            if not stage:
                return {
                    'success': False,
                    'message': 'Stage parameter is required'
                }

            # Pagination
            page = request.args.get("page", default=1, type=int)
            per_page = request.args.get("per_page", default=10, type=int)
            offset = (page - 1) * per_page

            

            # Main query using SQLAlchemy ORM
            query = (
                db.session.query(
                    func.any_value(ResearchData.data_id).label("data_id"),
                    func.any_value(ResearchData.organism_id).label("organism_id"),
                    func.any_value(Organism.organism_name).label("organism_name"),
                    func.any_value(Organism.organism_type).label("organism_type"),
                    func.coalesce(func.round(func.avg(OrganismRating.rating), 1), None).label("average_rating"),
                    func.count(distinct(OrganismRating.id)).label("review_count"),
                    func.count(
                        case(
                            [(func.length(OrganismRating.review) > 0, 1)],
                            else_=None
                        )
                    ).label("reviews_with_text"),
                    # Add the new group_concat here
                    # Modified group_concat - handle potential NULL values
                    func.group_concat(
                        distinct(
                            func.concat(
                                Protein.protein_name, 
                                '@', 
                                Compound.compound_name, 
                                '@',
                                case(
                                    [
                                        (Compound.pubchem_id.isnot(None), Compound.pubchem_id),
                                    ],
                                    else_= ''  # or use None if you prefer
                                ),
                                '@', 
                                case(
                                    [
                                        (MolecularModels.model_name.isnot(None), MolecularModels.model_name),
                                    ],
                                    else_= ''  # or use None if you prefer
                                )
                            )
                        )
                    ).label("compound_protein_model")
                )
                .outerjoin(Protein, Protein.protein_id == ResearchData.protein_id)
                .outerjoin(Compound, Compound.compound_id == ResearchData.compound_id)
                .outerjoin(Organism, Organism.organism_id == ResearchData.organism_id)
                .outerjoin(OrganismRating, OrganismRating.organism_id == Organism.organism_id)
                .outerjoin(
                    MolecularModels,
                    (MolecularModels.protein_id == Protein.protein_id) &
                    (MolecularModels.compound_id == Compound.compound_id)
                )
                .filter(ResearchData.stage_id == stage)
                .group_by(ResearchData.organism_id)
                .limit(per_page)
                .offset(offset)
            )
            
            # Print the raw SQL query for debugging
            # print(query.statement.compile(compile_kwargs={"literal_binds": True}))
            

            results = query.all()
            # return {
            #     'success': True,
            #     'results': total,
            #     'query': str(query.statement.compile(compile_kwargs={"literal_binds": True})),
            # }
            # Count total records
            total = (
                db.session.query(func.count(distinct(ResearchData.organism_id)))
                .filter(ResearchData.stage_id == stage)
                .scalar()
            )
            
            # SELECT research_data.data_id, research_data.organism_id, organisms.organism_name, 
            # organisms.organism_type, coalesce(round(avg(organism_ratings.rating), 1), NULL) AS average_rating, count(organism_ratings.id) AS review_count, 
            # count(CASE WHEN (length(organism_ratings.review) > 0) THEN 1 END) AS reviews_with_text, group_concat(DISTINCT concat(proteins.protein_name, '@', compounds.compound_name, '@', CASE WHEN 
            # (compounds.pubchem_id IS NOT NULL) THEN compounds.pubchem_id ELSE '' END, '@', CASE WHEN (molecular_models.file_path IS NOT NULL) THEN molecular_models.file_path ELSE '' END)) AS compound_protein_model 

            # FROM research_data 

            # LEFT OUTER JOIN proteins ON proteins.protein_id = research_data.protein_id 

            # LEFT OUTER JOIN compounds ON compounds.compound_id = research_data.compound_id 

            # LEFT OUTER JOIN organisms ON organisms.organism_id = research_data.organism_id 

            # LEFT OUTER JOIN organism_ratings ON organism_ratings.organism_id = organisms.organism_id 

            # LEFT OUTER JOIN molecular_models ON molecular_models.protein_id = proteins.protein_id AND molecular_models.compound_id = compounds.compound_id 

            # WHERE research_data.stage_id = '1' 

            # GROUP BY research_data.organism_id LIMIT 10 OFFSET 0;

            # Format the response with proper null handling
            formatted_results = []
            for row in results:
                data_id = row[0]
                # protein_name = row[1]
                # compound_name = row[1]
                organism_id = row[1]
                organism_name = row[2]
                organism_type = row[3]
                average_rating = row[4]
                review_count = row[5]
                reviews_with_text = row[6]
                compound_protein_model = row[7]

                # Parse the compound_protein_model string
                cpm_objects = parse_compound_protein_model(compound_protein_model)

                # Look up the common name (case-insensitive)
                common_name = get_english_name(organism_name)

                # if hasattr(research_data, "to_dict"):
                #     base_dict = research_data.to_dict()
                # else:
                #     base_dict = dict(research_data.__dict__)
                #     base_dict.pop('_sa_instance_state', None)  # Remove non-serializable attribute

                formatted_row = {
                    # **base_dict,
                    # 'protein_name': protein_name,
                    # 'compound_name': compound_name,
                    'data_id': data_id,
                    'organism_id': organism_id,
                    'organism_name': organism_name,
                    'organism_type': organism_type,
                    'food': common_name,
                    'compound_protein_model': cpm_objects,
                    'rating': {
                        'average_rating': float(average_rating) if average_rating is not None else None,
                        'review_count': review_count,
                        'reviews_with_text': reviews_with_text
                    } if review_count > 0 else None
                }
                formatted_results.append(formatted_row)

            # Sort by average_rating (highest first)
            formatted_results.sort(
                key=lambda x: (
                    -x['rating']['average_rating'] 
                    if x['rating'] and x['rating']['average_rating'] is not None 
                    else float('inf')
                )
            )
            
            # return {
            #     'success': True,
            #     'results': total,
            #     'query': str(query.statement.compile(compile_kwargs={"literal_binds": True})),
            # }

            return {
                'success': True,
                'data': formatted_results,
                'pagination': {
                    'total': total,
                    'page': page,
                    'per_page': per_page,
                    'total_pages': (total + per_page - 1) // per_page
                }
            }
            
        except Exception as e:
            # Add the raw query and error message to the error response for debugging
            return {
                'success': False,
                'message': str(e),
                'raw_query': str(query.statement.compile(compile_kwargs={"literal_binds": True})) if 'query' in locals() else None
            }, 500

# def parse_compound_protein_model(cpm_string):
#     if not cpm_string:
#         return []
    
#     result = []
#     for item in cpm_string.split(','):
#         parts = item.split('@')
#         if len(parts) >= 3:  # Ensure we have all three parts
#             obj = {
#                 'protein': parts[0].strip(),
#                 'compound': parts[1].strip(),
#                 'pubchem_id': parts[2].strip(),
#                 'model': parts[3].strip()
#             }
#             result.append(obj)
#     return result


# def get_english_name(scientific_name,  language="English"):
#     base_url = "https://sciname.info/Default.asp"
#     params = {"SciName": scientific_name}

#     response = requests.get(base_url, params=params)
#     soup = BeautifulSoup(response.content, "html.parser")

#     tables = soup.find_all("table")
#     results = []

#     for table in tables:
#         rows = table.find_all("tr")
#         for row in rows:
#             cells = row.find_all("td")
#             if len(cells) >= 2:
#                 key = cells[0].get_text(strip=True)
#                 val = cells[1].get_text(strip=True)
#                 if key.startswith(f"{language}:"):
#                     results.append(val)

#     return results


# @bp.route("/api/organisms/<int:organism_id>/reviews")
# @rest_api.route('/api/organisms/<organism_id>/reviews', endpoint='OrganismReviews')
# @rest_api.doc(params={'organism_id': 'Organism ID to fetch reviews'})

# class OrganismReviews(Resource):
#     def get(self, organism_id):
#         try:
#             # Fetch reviews using SQLAlchemy ORM
#             reviews = (
#                 db.session.query(OrganismRating)
#                 .filter(OrganismRating.organism_id == organism_id)
#                 .order_by(OrganismRating.created_at.desc())
#                 .all()
#             )

#             # Serialize reviews
#             reviews_list = []
#             for review in reviews:
#                 reviews_list.append({
#                     'id': review.id,
#                     'organism_id': review.organism_id,
#                     'rating': review.rating,
#                     'review': review.review,
#                     'reviewer_name': review.reviewer_name if review.reviewer_name else 'Anonymous',
#                     'reviewer_email': review.reviewer_email if review.reviewer_email else 'Anonymous',
#                     'created_at': review.created_at.isoformat() if review.created_at else None,
#                     'updated_at': review.updated_at.isoformat() if review.updated_at else None,
#                 })

#             # Calculate stats
#             stats = (
#                 db.session.query(
#                     func.avg(OrganismRating.rating).label('average_rating'),
#                     func.count(OrganismRating.id).label('review_count')
#                 )
#                 .filter(OrganismRating.organism_id == organism_id)
#                 .first()
#             )

#             average_rating = float(stats.average_rating) if stats.average_rating else 0
#             review_count = stats.review_count if stats.review_count else 0

#             return {
#                 'success': True,
#                 'data': {
#                     'reviews': reviews_list,
#                     'average_rating': average_rating,
#                     'review_count': review_count
#                 }
#             }
#         except Exception as e:
#             return {
#                 'success': False,
#                 'message': str(e),
#                 'data': {
#                     'reviews': [],
#                     'average_rating': 0,
#                     'review_count': 0
#                 }
#             }, 500

# Register the resource with the endpoint
# rest_api.add_resource(OrganismReviews, '/api/organisms/<organism_id>/reviews')


# @rest_api.route('/api/organisms/<int:organism_id>/rating')
# class AddOrganismRating(Resource):
#     """
#     Add a new rating for an organism (anonymous rating)
#     """

#     @rest_api.doc(params={'organism_id': 'Organism ID to add rating'})
#     @rest_api.expect({
#         'rating': fields.Integer(required=True, description='Rating value (1-5)'),
#         'review': fields.String(required=False, description='Optional review text'),
#         'user_name': fields.String(required=False, default='Anonymous', description='Reviewer name'),
#         'user_email': fields.String(required=False, default='Anonymous', description='Reviewer email')
#     })


#     def post(self, organism_id):
#         try:
#             data = request.get_json()

#             # Validate required fields
#             if not data or 'rating' not in data:
#                 return {
#                     'success': False,
#                     'message': 'Rating is required'
#                 }, 400

#             rating = data.get('rating')
#             review = data.get('review', '')
#             reviewer_name = data.get('user_name', 'Anonymous')
#             reviewer_email = data.get('user_email', 'Anonymous')

#             # Validate rating value
#             if not isinstance(rating, int) or rating < 1 or rating > 5:
#                 return {
#                     'success': False,
#                     'message': 'Rating must be an integer between 1 and 5'
#                 }, 400

#             # Insert new rating using SQLAlchemy
#             new_rating = OrganismRating(
#                 organism_id=organism_id,
#                 rating=rating,
#                 review=review,
#                 reviewer_name=reviewer_name,
#                 reviewer_email=reviewer_email,
#                 created_at=datetime.now(timezone.utc)
#             )
#             db.session.add(new_rating)
#             db.session.commit()

#             return {
#                 'success': True,
#                 'message': 'Rating added successfully',
#                 'rating_id': new_rating.id
#             }
#         except Exception as e:
#             db.session.rollback()
#             return {
#                 'success': False,
#                 'message': str(e)
#             }, 500



@rest_api.route('/api/protein-compound-upload')
class ProteinCompoundUpload(Resource):
    """
    Upload PDB file for a protein-compound pair
    """

    @token_required
    def post(self, current_user):
        try:
            # Get form data
            protein_id = request.form.get('protein')
            compound_id = request.form.get('compound')
            
            # Validate required fields
            if not protein_id or not compound_id:
                return {"success": False, "message": "Protein and Compound are required"}, 400
            
            # Check if file is present in the request
            if 'file' not in request.files:
                return {"success": False, "message": "No file provided"}, 400
            
            file = request.files['file']
            
            # Validate file
            if file.filename == '':
                return {"success": False, "message": "No file selected"}, 400
            
            # Validate file type (PDB file)
            if not (file.filename.endswith('.pdb') or 
                   file.content_type == 'chemical/x-pdb'):
                return {"success": False, "message": "Only PDB files are allowed"}, 400
            
            # Read and validate file content
            file_content = file.read().decode('utf-8')
            
            # Basic PDB file validation - check if it contains ATOM or HETATM records
            if "ATOM" not in file_content and "HETATM" not in file_content:
                return {"success": False, "message": "Invalid PDB file format"}, 400
            
            # Check if protein exists
            protein = Protein.query.get(protein_id)
            if not protein:
                return {"success": False, "message": "Invalid protein selected"}, 400
            
            # Check if compound exists
            compound = Compound.query.get(compound_id)
            if not compound:
                return {"success": False, "message": "Invalid compound selected"}, 400
            
            # Generate filename using convention: Protein Name + '_' + Compound Name
            protein_name = secure_filename(protein.protein_name)
            compound_name = secure_filename(compound.compound_name)
            filename = f"{protein_name}_{compound_name}.pdb"
            
            # Save file to storage with pdb_files subdirectory
            upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
            pdb_folder = os.path.join(upload_folder, current_app.config.get('PDB_FOLDER', 'pdb_files'))
            os.makedirs(pdb_folder, exist_ok=True)
            file_path = os.path.join(pdb_folder, filename)
            
            # Delete old file if it exists for the same protein-compound pair
            if os.path.exists(file_path):
                os.remove(file_path)
                current_app.logger.info(f"Deleted old file: {file_path}")
            
            # Save the new file
            with open(file_path, 'w') as f:
                f.write(file_content)
            
            # Create MolecularModels record
            molecular_data = MolecularModels(
                file_path=file_path,
                model_name=filename,
                protein_id=protein_id,
                compound_id=compound_id,
            )
            
            # Save to database
            molecular_data.save()
            
            return {
                "success": True, 
                "message": "PDB file uploaded successfully",
                "data_id": molecular_data.model_id,
                "file_path": file_path,
                "filename": filename
            }, 200
            
        except Exception as e:
            # Log the error for debugging
            current_app.logger.error(f"Error in ProteinCompoundUpload: {str(e)}")
            
            return {
                "success": False, 
                "message": f"An error occurred during upload: {str(e)}"
            }, 500


# csv_import_ns = Namespace('api/csv-import', description='CSV Import Operations')

@rest_api.route('/api/csv-import/import-research-data')
class ImportResearchData(Resource):
    """
    Imports research data from CSV into MySQL database with proper relationships
    """
    # @rest_api.doc('import_research_data')
    # def options(self):
    #     """Handle OPTIONS for CORS preflight"""
    #     return {'Allow': 'POST'}, 200, {
    #         'Access-Control-Allow-Origin': 'http://localhost:3000',
    #         'Access-Control-Allow-Methods': 'POST, OPTIONS',
    #         'Access-Control-Allow-Headers': 'Authorization, Content-Type'
    #     }
    
    @token_required
    def post(self, current_user):
        """
        Processes uploaded CSV file and imports data into database
        """
        
        # Check if file was uploaded
        if 'file' not in request.files:
            return {"success": False, "message": "No file uploaded"}, 400
            
        csv_file = request.files['file']
        
        if not csv_file.filename.endswith('.csv'):
            return {"success": False, "message": "File must be a CSV"}, 400
        
        try:
            # Read CSV file
            df = pd.read_csv(csv_file)
            
            # Process data in transaction
            with db.engine.begin() as connection:
                # Step 1: Process proteins
                ImportResearchData._import_proteins(connection, df)
                
                # Step 2: Process compounds
                ImportResearchData._import_compounds(connection, df)
                
                # Step 3: Process organisms
                ImportResearchData._import_organisms(connection, df)
                
                # Step 4: Process research_data
                ImportResearchData._import_research_data(connection, df)
            
            return {"success": True, "message": "Data imported successfully"}, 200
            
        except Exception as e:
            # current_app.logger.error(f"CSV import failed: {str(e)}")
            return {"success": False, "message": f"Import failed: {str(e)}"}, 500
    
    @staticmethod
    def _import_proteins(connection, df):
        """Helper method to import proteins - bulk approach"""
        proteins = df['Target'].unique()
        
        # Get existing proteins in one query
        existing_proteins = connection.execute(
            text("SELECT protein_name FROM proteins WHERE protein_name IN :proteins"),
            {"proteins": tuple(proteins)}
        ).fetchall()
        
        existing_proteins_set = {row[0] for row in existing_proteins}
        
        # Insert only new proteins
        new_proteins = [p for p in proteins if p not in existing_proteins_set]
        
        for protein in new_proteins:
            connection.execute(
                text("INSERT INTO proteins (protein_name) VALUES (:protein)"),
                {"protein": protein}
            )

    
    @staticmethod
    def _import_compounds(connection, df):
        """Helper method to import compounds - bulk approach"""
        compound_names = df['compound_name'].unique()
        
        # Get existing compounds in one query
        existing_compounds = connection.execute(
            text("SELECT compound_name FROM compounds WHERE compound_name IN :names"),
            {"names": tuple(compound_names)}
        ).fetchall()
        
        existing_compounds_set = {row[0] for row in existing_compounds}
        
        # Insert only new compounds
        for _, row in df.iterrows():
            compound_name = row['compound_name']
            
            if compound_name not in existing_compounds_set:
                connection.execute(
                    text("""INSERT INTO compounds 
                        (compound_name, compound_IUPAC) 
                        VALUES (:name, :iupac)"""),
                    {"name": compound_name, "iupac": row['iupac_name']}
                )
                # Add to existing set to avoid duplicates in the same batch
                existing_compounds_set.add(compound_name)

    
    @staticmethod
    def _import_organisms(connection, df):
        """Helper method to import organisms - bulk approach"""
        all_organisms = []
        
        # Collect all unique organisms from the dataframe
        for _, row in df.iterrows():
            # Handle NaN/empty values
            organism_value = row['organisms']
            
            # Check if the value is NaN (float) or empty
            if pd.isna(organism_value) or organism_value == '':
                continue  # Skip empty values
                
            # Convert to string and split
            organisms = str(organism_value).split('|')
            for organism in organisms:
                organism = organism.strip()
                if organism:  # Skip empty strings
                    all_organisms.append(organism)
        
        unique_organisms = list(set(all_organisms))
        
        if not unique_organisms:
            return
        
        # Create placeholders for IN clause
        placeholders = ', '.join(['%s'] * len(unique_organisms))
        
        # Use string formatting for the IN clause
        query = f"SELECT organism_name FROM organisms WHERE organism_name IN ({placeholders})"
        
        existing_organisms = connection.execute(
            query,
            tuple(unique_organisms)  # Pass as tuple of parameters
        ).fetchall()
        
        existing_organisms_set = {row[0] for row in existing_organisms}
        
        # Insert only new organisms
        new_organisms = [org for org in unique_organisms if org not in existing_organisms_set]
        
        for organism in new_organisms:
            connection.execute(
                """INSERT INTO organisms 
                (organism_name, organism_type) 
                VALUES (%s, %s)""",
                (organism, 'natural')
            )
    
    @staticmethod
    def _import_research_data(connection, df):
        """Helper method with bulk duplicate checking"""
        # First collect all potential combinations
        combinations_to_check = []
        combinations_data = []
        
        for index, row in df.iterrows():
            # Get protein_id and compound_id (same as before)
            protein_result = connection.execute(
                "SELECT protein_id FROM proteins WHERE protein_name = %s",
                (row['Target'],)
            )
            protein_id = protein_result.scalar()
            if not protein_id: continue
            
            compound_result = connection.execute(
                "SELECT compound_id FROM compounds WHERE compound_name = %s",
                (row['compound_name'],)
            )
            compound_id = compound_result.scalar()
            if not compound_id: continue
            
            organisms = [org.strip() for org in str(row['organisms']).split('|') if org.strip()]
            stages = [s.strip() for s in str(row['clinical_stage']).split(',') if s.strip()]
            
            for organism in organisms:
                organism_result = connection.execute(
                    "SELECT organism_id FROM organisms WHERE organism_name = %s",
                    (organism,)
                )
                organism_id = organism_result.scalar()
                if not organism_id: continue
                
                for stage in stages:
                    try:
                        stage_int = int(stage)
                        combinations_to_check.append((protein_id, compound_id, organism_id, stage_int, 1))
                        combinations_data.append((protein_id, compound_id, organism_id, stage_int, 1, index))
                    except ValueError:
                        print(f"Invalid stage value: {stage}")
        
        if not combinations_to_check:
            return
        
        # Check which combinations already exist
        existing_combinations = set()
        
        # Process in batches to avoid very long SQL queries
        batch_size = 100
        for i in range(0, len(combinations_to_check), batch_size):
            batch = combinations_to_check[i:i + batch_size]
            
            # Build query to check existing combinations
            placeholders = ', '.join(['(%s, %s, %s, %s, %s)'] * len(batch))
            params = []
            for combo in batch:
                params.extend(combo)
            
            existing_results = connection.execute(
                f"""SELECT protein_id, compound_id, organism_id, stage_id, country_id 
                FROM research_data 
                WHERE (protein_id, compound_id, organism_id, stage_id, country_id) IN ({placeholders})""",
                params
            ).fetchall()
            
            existing_combinations.update(existing_results)
        
        # Insert only non-existing combinations
        for combo_data in combinations_data:
            protein_id, compound_id, organism_id, stage_int, country_id, index = combo_data
            combo_tuple = (protein_id, compound_id, organism_id, stage_int, country_id)
            
            if combo_tuple not in existing_combinations:
                connection.execute(
                    """INSERT INTO research_data 
                    (protein_id, compound_id, organism_id, stage_id, country_id) 
                    VALUES (%s, %s, %s, %s, %s)""",
                    (protein_id, compound_id, organism_id, stage_int, country_id)
                )
            else:
                print(f"Row {index}: Research data already exists for combination {combo_tuple}")



# Absolute path is safer
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads", "pdb_files")
print(UPLOAD_FOLDER)

@rest_api.route("/api/pdb_files/<filename>")
class PdbFile(Resource):
    def get(self, filename):
        try:
            return send_from_directory(UPLOAD_FOLDER, filename)
        except FileNotFoundError:
            return {"error": "File not found"}, 404