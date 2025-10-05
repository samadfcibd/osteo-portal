"""
Organism Model
Represents biological organisms in the system
"""

from api.models.base_model import BaseModel
from api.db import db


class Organism(BaseModel):
    """
    Model representing biological organisms
    
    Attributes:
        organism_id (int): Primary key, auto-incrementing
        organism_name (str): Scientific name of the organism
        organism_type (str): Type of organism ('natural' or 'processed')
    """
    
    __tablename__ = 'organisms'
    
    organism_id = db.Column(
        db.Integer, 
        primary_key=True, 
        autoincrement=True,
        comment="Primary key, auto-incrementing organism identifier"
    )
    organism_name = db.Column(
        db.String(150), 
        nullable=False,
        unique=True,
        index=True,
        comment="Scientific name of the organism"
    )
    organism_type = db.Column(
        db.Enum('natural', 'processed', name='organism_type_enum'),
        nullable=False,
        default='natural',
        comment="Type of organism: natural or processed"
    )

    def __repr__(self):
        """
        String representation of the Organism instance
        
        Returns:
            str: String representation
        """
        return f"<Organism(organism_id={self.organism_id}, name='{self.organism_name}', type='{self.organism_type}')>"