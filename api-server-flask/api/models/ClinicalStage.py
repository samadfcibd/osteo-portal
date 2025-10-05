"""
Clinical Stage Model
Represents clinical trial stages in the system
"""

from api.models.base_model import BaseModel
from api.db import db


class ClinicalStage(BaseModel):
    """
    Model representing clinical trial stages
    
    Attributes:
        stage_id (int): Primary key, auto-incrementing
        stage_name (str): Name of the clinical stage
    """
    
    __tablename__ = 'clinical_stages'
    
    stage_id = db.Column(
        db.Integer, 
        primary_key=True, 
        autoincrement=True,
        comment="Primary key, auto-incrementing clinical stage identifier"
    )
    stage_name = db.Column(
        db.String(50), 
        nullable=False,
        unique=True,
        index=True,
        comment="Name of the clinical trial stage"
    )

    def __repr__(self):
        """
        String representation of the ClinicalStage instance
        
        Returns:
            str: String representation
        """
        return f"<ClinicalStage(stage_id={self.stage_id}, name='{self.stage_name}')>"

    @classmethod
    def get_all_stages(cls):
        """
        Get all clinical stages ordered by stage_id
        
        Returns:
            list: List of all ClinicalStage instances ordered by stage_id
            
        Raises:
            Exception: If database query fails
        """
        try:
            return cls.query.order_by(cls.stage_id).all()
        except Exception as e:
            # current_app.logger.error(f"Error fetching all clinical stages: {str(e)}")
            raise Exception("Failed to retrieve clinical stages") from e