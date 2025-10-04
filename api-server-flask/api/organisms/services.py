from datetime import datetime, timezone, timedelta
from flask import current_app
from api.models.ClinicalStage import ClinicalStage
from api.db import db

class OrganismService:
    @staticmethod
    def getAllClinicalStages():
        """Get all Clinical Stages"""
        return ClinicalStage.get_all_stages()