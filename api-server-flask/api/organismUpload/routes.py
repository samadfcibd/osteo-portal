"""
Organism Upload Routes
Handles CSV upload and import operations for research data
"""

from flask import Blueprint, request
from flask_restx import Resource, Namespace

from api.auth.decorators import token_required
from api.organismUpload.services import OrganismUploadService


# Initialize Blueprint and Namespace
organismUpload_ns_bp = Blueprint('organism_upload', __name__)
organismUpload_ns = Namespace('organism_upload', description='Organism upload operations')


@organismUpload_ns.route('/import-research-data')
class ImportResearchData(Resource):
    """
    Resource for importing research data from CSV files
    """
    
    @token_required
    def post(self, current_user):
        """
        Process uploaded CSV file and import data into database
        
        Returns:
            dict: Import results with success status and message
        """
        # Check if file was uploaded
        if 'file' not in request.files:
            return {
                "success": False, 
                "message": "No file uploaded"
            }, 400
            
        csv_file = request.files['file']
        
        # Validate file
        is_valid, error_message = OrganismUploadService.validate_csv_file(csv_file)
        if not is_valid:
            return {
                "success": False, 
                "message": error_message
            }, 400
        
        try:
            # Read CSV data
            df = OrganismUploadService.read_csv_data(csv_file)
            
            # Import data
            result = OrganismUploadService.import_research_data(df)
            
            return result, 200
            
        except ValueError as e:
            # Handle validation errors
            return {
                "success": False, 
                "message": str(e)
            }, 400
            
        except Exception as e:
            # Handle unexpected errors
            # current_app.logger.error(f"CSV import failed: {str(e)}")
            return {
                "success": False, 
                "message": f"Import failed: {str(e)}"
            }, 500