"""
Molecular Models Model
Represents molecular models and their associated files in the system
"""

from api.models.base_model import BaseModel
from api.db import db


class MolecularModels(BaseModel):
    """
    Model representing molecular models (PDB structures, etc.)
    
    Attributes:
        model_id (int): Primary key, auto-incrementing
        protein_id (int): Foreign key to proteins table
        compound_id (int): Foreign key to compounds table
        model_name (str): Name of the molecular model
        pdb_id (str): PDB database identifier
        file_path (str): Path to the model file
        resolution (float): Structure resolution in Angstroms
    """
    
    __tablename__ = 'molecular_models'
    
    model_id = db.Column(
        db.Integer, 
        primary_key=True, 
        autoincrement=True,
        comment="Primary key, auto-incrementing molecular model identifier"
    )
    protein_id = db.Column(
        db.Integer, 
        db.ForeignKey('proteins.protein_id', ondelete='CASCADE'),
        nullable=True,
        index=True,
        comment="Foreign key referencing the associated protein"
    )
    compound_id = db.Column(
        db.Integer, 
        db.ForeignKey('compounds.compound_id', ondelete='CASCADE'),
        nullable=True,
        index=True,
        comment="Foreign key referencing the associated compound"
    )
    model_name = db.Column(
        db.String(50), 
        nullable=False,
        comment="Descriptive name for the molecular model"
    )
    file_path = db.Column(
        db.String(255), 
        nullable=True,
        comment="File system path to the molecular model file"
    )

    def __repr__(self):
        """
        String representation of the MolecularModels instance
        
        Returns:
            str: String representation
        """
        return f"<MolecularModels(model_id={self.model_id}, name='{self.model_name}')>"