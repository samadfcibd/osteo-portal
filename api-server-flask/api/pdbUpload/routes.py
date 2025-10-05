"""
PDB Upload Routes
Handles PDB file uploads and retrieval operations
"""

from flask import Blueprint, request, send_from_directory
from flask_restx import Resource, Namespace

from api.auth.decorators import token_required
from api.pdbUpload.services import PDBUploadService


# Initialize Blueprint and Namespace
pdbUpload_bp = Blueprint('pdb_upload', __name__)
pdbUpload_ns = Namespace('pdb_upload', description='PDB upload operations')

@pdbUpload_ns.route('/proteins')
class Proteins(Resource):
    """Resource for handling protein operations"""
    
    def get(self):
        """
        Get all available proteins
        
        Returns:
            dict: Success status with list of proteins
        """
        try:
            result = PDBUploadService.get_all_proteins()
            return result, 200
            
        except Exception as e:
            return {
                'success': False,
                'message': 'Failed to fetch proteins'
            }, 500


@pdbUpload_ns.route('/compounds')
class Compounds(Resource):
    """Resource for handling compound operations"""
    
    def get(self):
        """
        Get all available compounds
        
        Returns:
            dict: Success status with list of compounds
        """
        try:
            result = PDBUploadService.get_all_compounds()
            return result, 200
            
        except Exception as e:
            return {
                'success': False,
                'message': 'Failed to fetch compounds'
            }, 500


@pdbUpload_ns.route('/protein-compound-upload')
class ProteinCompoundUpload(Resource):
    """Resource for handling PDB file uploads"""
    
    @token_required
    def post(self, _current_user):
        """
        Upload PDB file for a protein-compound pair
        
        Request Form Data:
            protein (int): Required protein ID
            compound (int): Required compound ID
            file (file): Required PDB file
            
        Returns:
            dict: Upload results with success status and file info
        """
        try:
            # Validate request
            is_valid, error_msg, status_code = PDBUploadService.validate_upload_request(
                request.form, request.files
            )
            if not is_valid:
                return {
                    "success": False, 
                    "message": error_msg
                }, status_code
            
            protein_id = request.form.get('protein')
            compound_id = request.form.get('compound')
            file = request.files['file']
            
            # Validate protein and compound exist
            is_valid, error_msg, status_code = PDBUploadService.validate_protein_compound_exists(
                protein_id, compound_id
            )
            if not is_valid:
                return {
                    "success": False, 
                    "message": error_msg
                }, status_code
            
            # Upload PDB file
            result = PDBUploadService.upload_pdb_file(protein_id, compound_id, file)
            
            return result, 200
            
        except ValueError as e:
            # Handle validation errors
            return {
                "success": False, 
                "message": str(e)
            }, 400
            
        except Exception as e:
            # Handle unexpected errors
            return {
                "success": False, 
                "message": f"An error occurred during upload: {str(e)}"
            }, 500

import os

UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads", "pdb_files")
@pdbUpload_ns.route("/pdb_files/<filename>")
class PdbFile(Resource):
    """Resource for serving PDB files"""


    def get(self, filename):
        try:
            return send_from_directory(UPLOAD_FOLDER, filename)
        except FileNotFoundError:
            return {"error": "File not found"}, 404
