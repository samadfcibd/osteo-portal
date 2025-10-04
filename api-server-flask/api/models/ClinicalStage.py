from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
# from api.db import db
from api.models.base_model import BaseModel


from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ClinicalStage(BaseModel):
    __tablename__ = 'clinical_stages'
    stage_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    stage_name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"Clinical Stage: {self.stage_name}"

    def save(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_all_stages(cls):
        return cls.query.all()