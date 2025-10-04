from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
# from api.db import db
from api.models.base_model import BaseModel


from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Protein(BaseModel):
    __tablename__ = 'proteins'
    protein_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    protein_name = db.Column(db.String(100), nullable=False)
    uniprot_id = db.Column(db.String(20), nullable=True)

    def __repr__(self):
        return f"Protein: {self.protein_name}"

    def save(self):
        db.session.add(self)
        db.session.commit()