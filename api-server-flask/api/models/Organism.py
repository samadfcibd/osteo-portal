from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
# from api.db import db
from api.models.base_model import BaseModel


from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Organism(BaseModel):
    __tablename__ = 'organisms'
    organism_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    organism_name = db.Column(db.String(150), nullable=True)
    organism_type = db.Column(db.Enum('natural', 'processed'), nullable=True)

    def __repr__(self):
        return f"Organism: {self.organism_name}"

    def save(self):
        db.session.add(self)
        db.session.commit()