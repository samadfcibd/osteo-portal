"""
Protein Model
Represents protein entities in the system
"""

from api.models.base_model import BaseModel
from api.db import db


class Protein(BaseModel):
    """
    Model representing protein entities
    
    Attributes:
        protein_id (int): Primary key, auto-incrementing
        protein_name (str): Name of the protein
        uniprot_id (str): UniProt database identifier
    """
    
    __tablename__ = 'proteins'
    
    protein_id = db.Column(
        db.Integer, 
        primary_key=True, 
        autoincrement=True,
        comment="Primary key, auto-incrementing protein identifier"
    )
    protein_name = db.Column(
        db.String(100), 
        nullable=False,
        unique=True,
        index=True,
        comment="Common or scientific name of the protein"
    )
    uniprot_id = db.Column(
        db.String(20), 
        nullable=True,
        unique=True,
        index=True,
        comment="UniProt database accession number"
    )

    def __repr__(self):
        """
        String representation of the Protein instance
        
        Returns:
            str: String representation
        """
        uniprot_info = f", UniProt: {self.uniprot_id}" if self.uniprot_id else ""
        return f"<Protein(protein_id={self.protein_id}, name='{self.protein_name}'{uniprot_info})>"