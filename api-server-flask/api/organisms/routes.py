from flask import Blueprint, request
from flask_restx import Api, Resource, fields, Namespace
from api.organisms.services import OrganismService
from api.db import db
from sqlalchemy import func, case, distinct, text
from api.models.ResearchData import ResearchData
from api.models.Organism import Organism
from api.models.OrganismRating import OrganismRating
from api.models.Protein import Protein
from api.models.Compound import Compound
from api.models.MolecularModels import MolecularModels
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta


organisms_bp = Blueprint('organisms', __name__)
organisms_ns = Namespace('organisms', description='Organism related operations')


@organisms_ns.route('/clinical-stages')
class ClinicalStages(Resource):
    def get(self):
        try:
            results = OrganismService.getAllClinicalStages()
            
            # Convert results to a list of dictionaries
            results = [{'stage_id': stage.stage_id, 'stage_name': stage.stage_name} for stage in results] 

            # Add the "Select stage" option at the beginning
            select_option = {
                'stage_id': '',
                'stage_name': 'Select stage'
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
  


@organisms_ns.route("/")
class Organisms(Resource):
    # @rest_api.doc(params={
    #     'stage': {'description': 'Stage ID', 'in': 'query', 'type': 'integer', 'required': True},
    #     'page': {'description': 'Page number for pagination', 'in': 'query', 'type': 'integer', 'required': False, 'default': 1},
    #     'per_page': {'description': 'Number of items per page', 'in': 'query', 'type': 'integer', 'required': False, 'default': 10}
    # })

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
        
    
def parse_compound_protein_model(cpm_string):
    if not cpm_string:
        return []
    
    result = []
    for item in cpm_string.split(','):
        parts = item.split('@')
        if len(parts) >= 3:  # Ensure we have all three parts
            obj = {
                'protein': parts[0].strip(),
                'compound': parts[1].strip(),
                'pubchem_id': parts[2].strip(),
                'model': parts[3].strip()
            }
            result.append(obj)
    return result


def get_english_name(scientific_name,  language="English"):
    base_url = "https://sciname.info/Default.asp"
    params = {"SciName": scientific_name}

    response = requests.get(base_url, params=params)
    soup = BeautifulSoup(response.content, "html.parser")

    tables = soup.find_all("table")
    results = []

    for table in tables:
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) >= 2:
                key = cells[0].get_text(strip=True)
                val = cells[1].get_text(strip=True)
                if key.startswith(f"{language}:"):
                    results.append(val)

    return results


@organisms_ns.route('/<organism_id>/reviews', endpoint='OrganismReviews')
class OrganismReviews(Resource):
    def get(self, organism_id):
        try:
            # Fetch reviews using SQLAlchemy ORM
            reviews = (
                db.session.query(OrganismRating)
                .filter(OrganismRating.organism_id == organism_id)
                .order_by(OrganismRating.created_at.desc())
                .all()
            )

            # Serialize reviews
            reviews_list = []
            for review in reviews:
                reviews_list.append({
                    'id': review.id,
                    'organism_id': review.organism_id,
                    'rating': review.rating,
                    'review': review.review,
                    'reviewer_name': review.reviewer_name if review.reviewer_name else 'Anonymous',
                    'reviewer_email': review.reviewer_email if review.reviewer_email else 'Anonymous',
                    'created_at': review.created_at.isoformat() if review.created_at else None,
                    'updated_at': review.updated_at.isoformat() if review.updated_at else None,
                })

            # Calculate stats
            stats = (
                db.session.query(
                    func.avg(OrganismRating.rating).label('average_rating'),
                    func.count(OrganismRating.id).label('review_count')
                )
                .filter(OrganismRating.organism_id == organism_id)
                .first()
            )

            average_rating = float(stats.average_rating) if stats.average_rating else 0
            review_count = stats.review_count if stats.review_count else 0

            return {
                'success': True,
                'data': {
                    'reviews': reviews_list,
                    'average_rating': average_rating,
                    'review_count': review_count
                }
            }
        except Exception as e:
            return {
                'success': False,
                'message': str(e),
                'data': {
                    'reviews': [],
                    'average_rating': 0,
                    'review_count': 0
                }
            }, 500


@organisms_ns.route('/<int:organism_id>/rating', endpoint='AddOrganismRating')
class AddOrganismRating(Resource):
    """
    Add a new rating for an organism (anonymous rating)
    """

    # @rest_api.doc(params={'organism_id': 'Organism ID to add rating'})
    # @rest_api.expect({
    #     'rating': fields.Integer(required=True, description='Rating value (1-5)'),
    #     'review': fields.String(required=False, description='Optional review text'),
    #     'user_name': fields.String(required=False, default='Anonymous', description='Reviewer name'),
    #     'user_email': fields.String(required=False, default='Anonymous', description='Reviewer email')
    # })


    def post(self, organism_id):
        try:
            data = request.get_json()

            # Validate required fields
            if not data or 'rating' not in data:
                return {
                    'success': False,
                    'message': 'Rating is required'
                }, 400

            rating = data.get('rating')
            review = data.get('review', '')
            reviewer_name = data.get('user_name', 'Anonymous')
            reviewer_email = data.get('user_email', 'Anonymous')

            # Validate rating value
            if not isinstance(rating, int) or rating < 1 or rating > 5:
                return {
                    'success': False,
                    'message': 'Rating must be an integer between 1 and 5'
                }, 400

            # Insert new rating using SQLAlchemy
            new_rating = OrganismRating(
                organism_id=organism_id,
                rating=rating,
                review=review,
                reviewer_name=reviewer_name,
                reviewer_email=reviewer_email,
                created_at=datetime.now(timezone.utc)
            )
            db.session.add(new_rating)
            db.session.commit()

            return {
                'success': True,
                'message': 'Rating added successfully',
                'rating_id': new_rating.id
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': str(e)
            }, 500

