from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
# from api.db import db
from api.models.base_model import BaseModel


from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Compound(BaseModel):
    __tablename__ = 'compounds'
    compound_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    compound_name = db.Column(db.String(100), nullable=False)
    pubchem_id = db.Column(db.String(20), nullable=True)
    compound_IUPAC = db.Column(db.Text(), nullable=False)

    def __repr__(self):
        return f"Compound: {self.compound_name}"

    def save(self):
        db.session.add(self)
        db.session.commit()