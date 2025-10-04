from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
# from api.db import db
from api.models.base_model import BaseModel


from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class OrganismRating(BaseModel):
    __tablename__ = 'organism_ratings'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    organism_id = db.Column(db.Integer(), db.ForeignKey('organisms.organism_id'), nullable=False)
    rating = db.Column(db.Integer(), nullable=False)
    review = db.Column(db.Text(), nullable=True)
    reviewer_name = db.Column(db.String(255), nullable=True, default='Anonymous')
    reviewer_email = db.Column(db.String(255), nullable=True, default='Anonymous')
    created_at = db.Column(db.DateTime(), nullable=True, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(), nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"OrganismRating: {self.id} for Organism {self.organism_id}"

    def save(self):
        db.session.add(self)
        db.session.commit()