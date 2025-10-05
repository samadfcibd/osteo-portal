"""
Organism Rating Model
Represents user ratings and reviews for organisms in the system
"""

from datetime import datetime, timezone
from api.models.base_model import BaseModel
from api.db import db


class OrganismRating(BaseModel):
    """
    Model representing user ratings and reviews for organisms
    
    Attributes:
        id (int): Primary key, auto-incrementing
        organism_id (int): Foreign key to organisms table
        rating (int): User rating value (1-5)
        review (str): Optional review text
        reviewer_name (str): Name of the reviewer
        reviewer_email (str): Email of the reviewer
    """
    
    __tablename__ = 'organism_ratings'
    
    id = db.Column(
        db.Integer, 
        primary_key=True, 
        autoincrement=True,
        comment="Primary key, auto-incrementing rating identifier"
    )
    organism_id = db.Column(
        db.Integer, 
        db.ForeignKey('organisms.organism_id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment="Foreign key referencing the rated organism"
    )
    rating = db.Column(
        db.Integer, 
        nullable=False,
        comment="User rating value from 1 to 5"
    )
    review = db.Column(
        db.Text, 
        nullable=True,
        comment="Optional detailed review text from the user"
    )
    reviewer_name = db.Column(
        db.String(255), 
        nullable=True,
        default='Anonymous',
        comment="Name of the person submitting the rating"
    )
    reviewer_email = db.Column(
        db.String(255), 
        nullable=True,
        default='Anonymous',
        comment="Email address of the person submitting the rating"
    )

    def __repr__(self):
        """
        String representation of the OrganismRating instance
        
        Returns:
            str: String representation
        """
        review_preview = f", Review: '{self.review[:30]}...'" if self.review else ""
        return f"<OrganismRating(id={self.id}, organism_id={self.organism_id}, rating={self.rating}{review_preview})>"