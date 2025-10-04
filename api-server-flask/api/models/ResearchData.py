from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
# from api.db import db
from api.models.base_model import BaseModel


from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ResearchData(BaseModel):
    __tablename__ = 'research_data'
    data_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    stage_id = db.Column(db.Integer(), db.ForeignKey('clinical_stages.stage_id'), nullable=False)
    protein_id = db.Column(db.Integer(), db.ForeignKey('proteins.protein_id'), nullable=False)
    compound_id = db.Column(db.Integer(), db.ForeignKey('compounds.compound_id'), nullable=False)
    organism_id = db.Column(db.Integer(), db.ForeignKey('organisms.organism_id'), nullable=False)
    country_id = db.Column(db.Integer(), nullable=False)
    model_id = db.Column(db.Integer(), nullable=True)

    def __repr__(self):
        return f"ResearchData: {self.data_id}"

    def save(self):
        db.session.add(self)
        db.session.commit()