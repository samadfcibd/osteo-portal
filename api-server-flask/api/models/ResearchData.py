"""
Research Data Model
Represents the core research data linking proteins, compounds, organisms, and clinical stages
"""

from api.models.base_model import BaseModel
from api.db import db


class ResearchData(BaseModel):
    """
    Model representing research data relationships
    
    Attributes:
        data_id (int): Primary key, auto-incrementing
        stage_id (int): Foreign key to clinical_stages table
        protein_id (int): Foreign key to proteins table
        compound_id (int): Foreign key to compounds table
        organism_id (int): Foreign key to organisms table
        country_id (int): Country identifier
        model_id (int): Optional foreign key to molecular_models table
    """
    
    __tablename__ = 'research_data'
    
    data_id = db.Column(
        db.Integer, 
        primary_key=True, 
        autoincrement=True,
        comment="Primary key, auto-incrementing research data identifier"
    )
    stage_id = db.Column(
        db.Integer, 
        db.ForeignKey('clinical_stages.stage_id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Foreign key referencing the clinical trial stage"
    )
    protein_id = db.Column(
        db.Integer, 
        db.ForeignKey('proteins.protein_id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Foreign key referencing the protein"
    )
    compound_id = db.Column(
        db.Integer, 
        db.ForeignKey('compounds.compound_id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Foreign key referencing the compound"
    )
    organism_id = db.Column(
        db.Integer, 
        db.ForeignKey('organisms.organism_id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Foreign key referencing the organism"
    )
    country_id = db.Column(
        db.Integer, 
        nullable=False,
        index=True,
        comment="Identifier for the country/origin of research"
    )
    model_id = db.Column(
        db.Integer, 
        nullable=True,
        index=True,
        comment="Optional foreign key referencing molecular models"
    )
    
    # Define composite unique constraint to prevent duplicate entries
    __table_args__ = (
        db.UniqueConstraint('stage_id', 'protein_id', 'compound_id', 'organism_id', 'country_id',
                          name='uq_research_data_composite'),
    )

    def __repr__(self):
        """
        String representation of the ResearchData instance
        
        Returns:
            str: String representation
        """
        model_info = f", Model: {self.model_id}" if self.model_id else ""
        return f"<ResearchData(data_id={self.data_id}, Stage: {self.stage_id}, Protein: {self.protein_id}, Compound: {self.compound_id}, Organism: {self.organism_id}{model_info})>"