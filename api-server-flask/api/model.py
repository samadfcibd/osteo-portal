# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from datetime import datetime

import json

from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Users(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(32), nullable=False)
    email = db.Column(db.String(64), nullable=True)
    password = db.Column(db.Text())
    jwt_auth_active = db.Column(db.Boolean())
    date_joined = db.Column(db.DateTime(), default=datetime.utcnow)

    def __repr__(self):
        return f"User {self.username}"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def update_email(self, new_email):
        self.email = new_email

    def update_username(self, new_username):
        self.username = new_username

    def check_jwt_auth_active(self):
        return self.jwt_auth_active

    def set_jwt_auth_active(self, set_status):
        self.jwt_auth_active = set_status

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)

    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def get_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    def toDICT(self):

        cls_dict = {}
        cls_dict['_id'] = self.id
        cls_dict['username'] = self.username
        cls_dict['email'] = self.email

        return cls_dict

    def toJSON(self):

        return self.toDICT()


class JWTTokenBlocklist(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    jwt_token = db.Column(db.String(), nullable=False)
    created_at = db.Column(db.DateTime(), nullable=False)

    def __repr__(self):
        return f"Expired Token: {self.jwt_token}"

    def save(self):
        db.session.add(self)
        db.session.commit()


class ClinicalStage(db.Model):
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
    

class Protein(db.Model):
    __tablename__ = 'proteins'
    protein_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    protein_name = db.Column(db.String(100), nullable=False)
    uniprot_id = db.Column(db.String(20), nullable=True)

    def __repr__(self):
        return f"Protein: {self.protein_name}"

    def save(self):
        db.session.add(self)
        db.session.commit()


class Organism(db.Model):
    __tablename__ = 'organisms'
    organism_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    organism_name = db.Column(db.String(150), nullable=True)
    organism_type = db.Column(db.Enum('natural', 'processed'), nullable=True)

    def __repr__(self):
        return f"Organism: {self.organism_name}"

    def save(self):
        db.session.add(self)
        db.session.commit()


class Compound(db.Model):
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


class ResearchData(db.Model):
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


class OrganismRating(db.Model):
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

class MolecularModels(db.Model):
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