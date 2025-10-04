from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
# from api.db import db
from api.models.base_model import BaseModel


from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class MolecularModels(BaseModel):
    __tablename__ = 'molecular_models'
    model_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    protein_id = db.Column(db.Integer(), db.ForeignKey('proteins.protein_id'), nullable=True)
    compound_id = db.Column(db.Integer(), db.ForeignKey('compounds.compound_id'), nullable=True)
    model_name = db.Column(db.String(50), nullable=False)
    pdb_id = db.Column(db.String(10), nullable=True)
    file_path = db.Column(db.String(255), nullable=True)
    resolution = db.Column(db.Float(), nullable=True)

    def __repr__(self):
        return f"MolecularModel: {self.model_name}"

    def save(self):
        db.session.add(self)
        db.session.commit()