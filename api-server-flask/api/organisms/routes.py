"""
Organisms Blueprint
Handles organism-related API routes
"""

from flask import Blueprint, request
from flask_restx import Resource, Namespace

from api.organisms.services import OrganismService

# Initialize Blueprint and Namespace
organisms_bp = Blueprint('organisms', __name__)
organisms_ns = Namespace('organisms', description='Organism related operations')


@organisms_ns.route('/clinical-stages')
class ClinicalStages(Resource):
    """Resource for handling clinical stages operations"""
    
    def get(self):
        """
        Get all available clinical stages
        
        Returns:
            dict: Success status with list of clinical stages
        """
        try:
            results = OrganismService.get_all_clinical_stages()
            
            # Convert results to a list of dictionaries
            stages_list = [
                {
                    'stage_id': stage.stage_id, 
                    'stage_name': stage.stage_name
                } for stage in results
            ]

            # Add the "Select stage" option at the beginning
            select_option = {
                'stage_id': '',
                'stage_name': 'Select stage'
            }
            stages_list.insert(0, select_option)
            
            return {
                'success': True,
                'data': stages_list
            }, 200
        
        except Exception as e:
            return {
                'success': False,
                'message': 'Failed to fetch clinical stages'
            }, 500


@organisms_ns.route("/")
class Organisms(Resource):
    """Resource for handling organism listings with filtering and pagination"""
    
    def get(self):
        """
        Get paginated list of organisms filtered by clinical stage
        """
        try:
            stage = request.args.get("stage")
            
            # Validate required parameter
            if not stage:
                return {
                    'success': False,
                    'message': 'Stage parameter is required'
                }, 400
            
            # Validate stage is numeric
            if not stage.isdigit():
                return {
                    'success': False,
                    'message': 'Stage parameter must be a valid integer'
                }, 400

            # Pagination parameters
            page = request.args.get("page", default=OrganismService.DEFAULT_PAGE, type=int)
            per_page = request.args.get("per_page", default=OrganismService.DEFAULT_PER_PAGE, type=int)
            
            # Validate pagination parameters
            if page < 1:
                return {
                    'success': False,
                    'message': 'Page must be a positive integer'
                }, 400
                
            if per_page < 1 or per_page > OrganismService.MAX_PER_PAGE:
                return {
                    'success': False,
                    'message': f'Per_page must be between 1 and {OrganismService.MAX_PER_PAGE}'
                }, 400

            # Get data from service
            formatted_results, total = OrganismService.get_organisms_by_stage(
                int(stage), page, per_page
            )

            return {
                'success': True,
                'data': formatted_results,
                'pagination': {
                    'total': total,
                    'page': page,
                    'per_page': per_page,
                    'total_pages': (total + per_page - 1) // per_page if total > 0 else 0
                }
            }, 200
            
        except Exception as e:
            return {
                'success': False,
                'message': 'Failed to fetch organisms data'
            }, 500


@organisms_ns.route('/<organism_id>/reviews', endpoint='OrganismReviews')
class OrganismReviews(Resource):
    """Resource for handling organism reviews"""

    def get(self, organism_id):
        """
        Get all reviews for a specific organism
        """
        try:
            # Validate organism_id is numeric
            if not organism_id.isdigit():
                return {
                    'success': False,
                    'message': 'Invalid organism ID'
                }, 400
            
            reviews_data = OrganismService.get_organism_reviews(int(organism_id))
            
            return {
                'success': True,
                'data': reviews_data
            }, 200
            
        except Exception as e:
            return {
                'success': False,
                'message': 'Failed to fetch reviews',
                'data': {
                    'reviews': [],
                    'average_rating': 0,
                    'review_count': 0
                }
            }, 500


@organisms_ns.route('/<int:organism_id>/rating', endpoint='AddOrganismRating')
class AddOrganismRating(Resource):
    """Resource for adding organism ratings and reviews"""

    def post(self, organism_id):
        """
        Add a new rating for an organism
        """
        try:
            data = request.get_json()

            # Validate request body
            if not data:
                return {
                    'success': False,
                    'message': 'Request body is required'
                }, 400

            # Validate required fields
            if 'rating' not in data:
                return {
                    'success': False,
                    'message': 'Rating is required'
                }, 400

            # Add rating through service
            rating_id = OrganismService.add_organism_rating(organism_id, data)

            return {
                'success': True,
                'message': 'Rating added successfully',
                'rating_id': rating_id
            }, 201
            
        except ValueError as e:
            return {
                'success': False,
                'message': str(e)
            }, 400
        except Exception as e:
            return {
                'success': False,
                'message': 'Failed to add rating'
            }, 500