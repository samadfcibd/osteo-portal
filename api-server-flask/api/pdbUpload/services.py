"""
PDB Upload Service
Handles business logic for PDB file uploads and management
"""

import os
from werkzeug.utils import secure_filename
from flask import current_app

from api.models.Protein import Protein
from api.models.Compound import Compound
from api.models.MolecularModels import MolecularModels
from api.db import db


class PDBUploadService:
    """Service class for PDB upload operations"""
    
    # Constants
    ALLOWED_EXTENSIONS = {'.pdb'}
    ALLOWED_MIME_TYPES = {'chemical/x-pdb', 'text/plain'}
    UPLOAD_SUBFOLDER = 'pdb_files'
    
    @staticmethod
    def get_all_proteins():
        """
        Retrieve all proteins with select option
        
        Returns:
            dict: Success status with proteins data
        """
        try:
            results = Protein.query.all()
            
            proteins_list = [
                {
                    'protein_id': protein.protein_id, 
                    'protein_name': protein.protein_name
                } for protein in results
            ]

            # Add select option
            select_option = {
                'protein_id': '',
                'protein_name': 'Select protein'
            }
            proteins_list.insert(0, select_option)
            
            return {
                'success': True,
                'data': proteins_list
            }
            
        except Exception as e:
            current_app.logger.error(f"Error fetching proteins: {str(e)}")
            raise Exception("Failed to fetch proteins")

    @staticmethod
    def get_all_compounds():
        """
        Retrieve all unique compounds with select option
        
        Returns:
            dict: Success status with compounds data
        """
        try:
            results = Compound.query.distinct(Compound.compound_name).all()
            
            compounds_list = [
                {
                    'compound_id': compound.compound_id, 
                    'compound_name': compound.compound_name
                } for compound in results
            ]

            # Add select option
            select_option = {
                'compound_id': '',
                'compound_name': 'Select compound'
            }
            compounds_list.insert(0, select_option)
            
            return {
                'success': True,
                'data': compounds_list
            }
            
        except Exception as e:
            current_app.logger.error(f"Error fetching compounds: {str(e)}")
            raise Exception("Failed to fetch compounds")

    @staticmethod
    def validate_upload_request(form_data, files):
        """
        Validate PDB upload request
        
        Args:
            form_data: Request form data
            files: Request files data
            
        Returns:
            tuple: (is_valid, error_message, status_code)
        """
        # Check required fields
        protein_id = form_data.get('protein')
        compound_id = form_data.get('compound')
        
        if not protein_id or not compound_id:
            return False, "Protein and Compound are required", 400
        
        # Check file presence
        if 'file' not in files:
            return False, "No file provided", 400
        
        file = files['file']
        
        if file.filename == '':
            return False, "No file selected", 400
        
        # Validate file type
        is_valid, error_msg = PDBUploadService._validate_file_type(file)
        if not is_valid:
            return False, error_msg, 400
        
        return True, "", 200

    @staticmethod
    def _validate_file_type(file):
        """
        Validate PDB file type and content
        
        Args:
            file: File object to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        # Check file extension
        filename = file.filename.lower()
        valid_extension = any(filename.endswith(ext) for ext in PDBUploadService.ALLOWED_EXTENSIONS)
        
        # Check MIME type
        valid_mime_type = file.content_type in PDBUploadService.ALLOWED_MIME_TYPES
        
        if not (valid_extension or valid_mime_type):
            return False, "Only PDB files are allowed"
        
        # Validate file content
        try:
            file_content = file.read().decode('utf-8')
            file.seek(0)  # Reset file pointer for later use
            
            # Basic PDB format validation
            if "ATOM" not in file_content and "HETATM" not in file_content:
                return False, "Invalid PDB file format - must contain ATOM or HETATM records"
                
        except UnicodeDecodeError:
            return False, "File must be UTF-8 encoded text"
        except Exception as e:
            current_app.logger.error(f"Error reading file content: {str(e)}")
            return False, "Error reading file content"
        
        return True, ""

    @staticmethod
    def validate_protein_compound_exists(protein_id, compound_id):
        """
        Validate that protein and compound exist in database
        
        Args:
            protein_id: Protein ID to validate
            compound_id: Compound ID to validate
            
        Returns:
            tuple: (is_valid, error_message, status_code)
        """
        try:
            protein = Protein.query.get(protein_id)
            if not protein:
                return False, "Invalid protein selected", 400
            
            compound = Compound.query.get(compound_id)
            if not compound:
                return False, "Invalid compound selected", 400
            
            return True, "", 200
            
        except Exception as e:
            current_app.logger.error(f"Error validating protein/compound: {str(e)}")
            return False, "Error validating selection", 500

    @staticmethod
    def upload_pdb_file(protein_id, compound_id, file):
        """
        Upload and save PDB file for protein-compound pair
        
        Args:
            protein_id: Protein ID
            compound_id: Compound ID
            file: PDB file object
            
        Returns:
            dict: Upload results with file info
            
        Raises:
            Exception: If upload fails
        """
        try:
            # Get protein and compound names
            protein = Protein.query.get(protein_id)
            compound = Compound.query.get(compound_id)
            
            if not protein or not compound:
                raise ValueError("Invalid protein or compound ID")
            
            # Read file content
            file_content = file.read().decode('utf-8')
            
            # Generate secure filename
            filename = PDBUploadService._generate_filename(protein.protein_name, compound.compound_name)
            
            # Save file to storage
            file_path, relative_file_path = PDBUploadService._save_file_to_storage(filename, file_content)
            
            # Update or create MolecularModels record
            molecular_data = PDBUploadService._update_molecular_models(
                protein_id, compound_id, relative_file_path, filename
            )
            
            return {
                "success": True,
                "message": "PDB file uploaded successfully",
                "data_id": molecular_data.model_id,
                "file_path": file_path,
                "filename": filename,
                "relative_path": relative_file_path
            }
            
        except Exception as e:
            current_app.logger.error(f"Error uploading PDB file: {str(e)}")
            raise Exception(f"Upload failed: {str(e)}")

    @staticmethod
    def _generate_filename(protein_name, compound_name):
        """
        Generate secure filename using convention: ProteinName_CompoundName.pdb
        
        Args:
            protein_name: Name of the protein
            compound_name: Name of the compound
            
        Returns:
            str: Generated filename
        """
        safe_protein_name = secure_filename(protein_name)
        safe_compound_name = secure_filename(compound_name)
        return f"{safe_protein_name}_{safe_compound_name}.pdb"

    @staticmethod
    def _save_file_to_storage(filename, file_content):
        """
        Save PDB file to storage system
        
        Args:
            filename: Name of the file to save
            file_content: Content of the file
            
        Returns:
            tuple: (absolute_file_path, relative_file_path)
        """
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        pdb_folder = os.path.join(upload_folder, PDBUploadService.UPLOAD_SUBFOLDER)
        
        # Create directory if it doesn't exist
        os.makedirs(pdb_folder, exist_ok=True)
        
        # Define file paths
        absolute_file_path = os.path.join(pdb_folder, filename)
        # Ensure relative path is always relative to the project root
        relative_file_path = os.path.join('uploads', PDBUploadService.UPLOAD_SUBFOLDER, filename)
        
        # Delete old file if it exists
        if os.path.exists(absolute_file_path):
            os.remove(absolute_file_path)
            current_app.logger.info(f"Deleted old file: {absolute_file_path}")
        
        # Save the new file
        with open(absolute_file_path, 'w', encoding='utf-8') as f:
            f.write(file_content)
        
        return absolute_file_path, relative_file_path

    @staticmethod
    def _update_molecular_models(protein_id, compound_id, file_path, model_name):
        """
        Update or create MolecularModels record
        
        Args:
            protein_id: Protein ID
            compound_id: Compound ID
            file_path: Path to the PDB file
            model_name: Name of the model
            
        Returns:
            MolecularModels: The created or updated model record
        """
        # Find existing record
        molecular_data = MolecularModels.query.filter_by(
            protein_id=protein_id,
            compound_id=compound_id
        ).first()

        if molecular_data:
            # Update existing record
            molecular_data.file_path = file_path
            molecular_data.model_name = model_name
            db.session.merge(molecular_data)
        else:
            # Create new record
            molecular_data = MolecularModels(
                file_path=file_path,
                model_name=model_name,
                protein_id=protein_id,
                compound_id=compound_id,
            )
            db.session.add(molecular_data)
        
        # Commit changes
        db.session.commit()
        
        return molecular_data