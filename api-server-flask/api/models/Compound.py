"""
Compound Model
Represents chemical compounds in the system
"""

from api.models.base_model import BaseModel
from api.db import db


class Compound(BaseModel):
    """
    Model representing chemical compounds
    
    Attributes:
        compound_id (int): Primary key, auto-incrementing
        compound_name (str): Name of the compound
        pubchem_id (str): PubChem identifier (nullable)
        compound_IUPAC (str): IUPAC name of the compound
    """
    
    __tablename__ = 'compounds'
    
    compound_id = db.Column(
        db.Integer, 
        primary_key=True, 
        autoincrement=True,
        comment="Primary key, auto-incrementing compound identifier"
    )
    compound_name = db.Column(
        db.String(100), 
        nullable=False,
        unique=True,
        index=True,
        comment="Common name of the chemical compound"
    )
    pubchem_id = db.Column(
        db.String(20), 
        nullable=True,
        unique=True,
        index=True,
        comment="PubChem compound identifier (CID)"
    )
    compound_IUPAC = db.Column(
        db.Text, 
        nullable=False,
        comment="IUPAC systematic name of the compound"
    )

    def __repr__(self):
        """
        String representation of the Compound instance
        
        Returns:
            str: String representation
        """
        pubchem_info = f", PubChem: {self.pubchem_id}" if self.pubchem_id else ""
        return f"<Compound(compound_id={self.compound_id}, name='{self.compound_name}'{pubchem_info})>"
