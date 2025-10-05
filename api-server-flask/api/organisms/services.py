"""
Organism Service
Handles business logic for organism-related operations including queries, ratings, and data processing
"""

from datetime import datetime, timezone
from flask import current_app
from sqlalchemy import func, case, distinct

from api.models.ClinicalStage import ClinicalStage
from api.models.ResearchData import ResearchData
from api.models.Organism import Organism
from api.models.OrganismRating import OrganismRating
from api.models.Protein import Protein
from api.models.Compound import Compound
from api.models.MolecularModels import MolecularModels
from api.db import db


class OrganismService:
    """Service class for organism-related business logic operations"""
    
    # Constants
    DEFAULT_PAGE = 1
    DEFAULT_PER_PAGE = 10
    MAX_PER_PAGE = 100
    MIN_RATING = 1
    MAX_RATING = 5
    ANONYMOUS_USER = 'Anonymous'

    @staticmethod
    def get_all_clinical_stages():
        """
        Retrieve all clinical stages from the database
        
        Returns:
            list: List of ClinicalStage objects ordered by stage_id
            
        Raises:
            Exception: If database query fails
        """
        try:
            stages = ClinicalStage.get_all_stages()
            # current_app.logger.info(f"Retrieved {len(stages)} clinical stages")
            return stages
        except Exception as e:
            # current_app.logger.error(f"Error retrieving clinical stages: {str(e)}")
            raise Exception("Failed to retrieve clinical stages") from e

    @staticmethod
    def get_organisms_by_stage(stage_id: int, page: int = 1, per_page: int = 10):
        """
        Retrieve paginated organisms for a specific clinical stage
        
        Args:
            stage_id (int): Clinical stage ID to filter by
            page (int): Page number for pagination
            per_page (int): Number of items per page
            
        Returns:
            tuple: (formatted_results, total_count) for pagination
            
        Raises:
            Exception: If database query fails
        """
        try:
            offset = (page - 1) * per_page

            # Main query using SQLAlchemy ORM
            query = (
                db.session.query(
                    func.any_value(ResearchData.data_id).label("data_id"),
                    func.any_value(ResearchData.organism_id).label("organism_id"),
                    func.any_value(Organism.organism_name).label("organism_name"),
                    func.any_value(Organism.organism_type).label("organism_type"),
                    func.coalesce(func.round(func.avg(OrganismRating.rating), 1), None).label("average_rating"),
                    func.count(distinct(OrganismRating.id)).label("review_count"),
                    func.count(
                        case(
                            [(func.length(OrganismRating.review) > 0, 1)],
                            else_=None
                        )
                    ).label("reviews_with_text"),
                    func.group_concat(
                        distinct(
                            func.concat(
                                Protein.protein_name, 
                                '@', 
                                Compound.compound_name, 
                                '@',
                                case(
                                    [(Compound.pubchem_id.isnot(None), Compound.pubchem_id)],
                                    else_= ''
                                ),
                                '@', 
                                case(
                                    [(MolecularModels.model_name.isnot(None), MolecularModels.model_name)],
                                    else_= ''
                                )
                            )
                        )
                    ).label("compound_protein_model")
                )
                .outerjoin(Protein, Protein.protein_id == ResearchData.protein_id)
                .outerjoin(Compound, Compound.compound_id == ResearchData.compound_id)
                .outerjoin(Organism, Organism.organism_id == ResearchData.organism_id)
                .outerjoin(OrganismRating, OrganismRating.organism_id == Organism.organism_id)
                .outerjoin(
                    MolecularModels,
                    (MolecularModels.protein_id == Protein.protein_id) &
                    (MolecularModels.compound_id == Compound.compound_id)
                )
                .filter(ResearchData.stage_id == stage_id)
                .group_by(ResearchData.organism_id)
                .limit(per_page)
                .offset(offset)
            )
            
            results = query.all()
            
            # Count total records
            total = (
                db.session.query(func.count(distinct(ResearchData.organism_id)))
                .filter(ResearchData.stage_id == stage_id)
                .scalar()
            )
            
            # Format the response
            formatted_results = OrganismService._format_organism_results(results)
            
            return formatted_results, total
            
        except Exception as e:
            # current_app.logger.error(f"Error fetching organisms for stage {stage_id}: {str(e)}")
            raise Exception("Failed to fetch organisms data") from e

    @staticmethod
    def _format_organism_results(results):
        """
        Format raw database results into structured response
        
        Args:
            results: Raw SQLAlchemy query results
            
        Returns:
            list: Formatted organism data
        """
        formatted_results = []
        
        for row in results:
            data_id = row[0]
            organism_id = row[1]
            organism_name = row[2]
            organism_type = row[3]
            average_rating = row[4]
            review_count = row[5]
            reviews_with_text = row[6]
            compound_protein_model = row[7]

            # Parse the compound_protein_model string
            cpm_objects = OrganismService.parse_compound_protein_model(compound_protein_model)

            formatted_row = {
                'data_id': data_id,
                'organism_id': organism_id,
                'organism_name': organism_name,
                'organism_type': organism_type,
                'food': '',  # Common name could be added here if needed
                'compound_protein_model': cpm_objects,
                'rating': {
                    'average_rating': float(average_rating) if average_rating is not None else None,
                    'review_count': review_count,
                    'reviews_with_text': reviews_with_text
                } if review_count > 0 else None
            }
            formatted_results.append(formatted_row)

        # Sort by average_rating (highest first)
        formatted_results.sort(
            key=lambda x: (
                -x['rating']['average_rating'] 
                if x['rating'] and x['rating']['average_rating'] is not None 
                else float('inf')
            )
        )
        
        return formatted_results

    @staticmethod
    def parse_compound_protein_model(cpm_string: str) -> list:
        """
        Parse compound_protein_model string into structured objects
        
        Args:
            cpm_string (str): Comma-separated string of protein@compound@pubchem_id@model
            
        Returns:
            list: List of dictionaries with parsed components
        """
        if not cpm_string:
            return []
        
        result = []
        try:
            for item in cpm_string.split(','):
                parts = item.split('@')
                if len(parts) >= 3:  # Ensure we have all three parts
                    obj = {
                        'protein': parts[0].strip(),
                        'compound': parts[1].strip(),
                        'pubchem_id': parts[2].strip(),
                        'model': parts[3].strip() if len(parts) > 3 else ''
                    }
                    result.append(obj)
        except Exception as e:
            # current_app.logger.error(f"Error parsing compound_protein_model: {str(e)}")
            return []
        
        return result

    @staticmethod
    def get_organism_reviews(organism_id: int):
        """
        Get all reviews and statistics for a specific organism
        
        Args:
            organism_id (int): Organism ID to fetch reviews for
            
        Returns:
            dict: Reviews data with statistics
            
        Raises:
            Exception: If database query fails
        """
        try:
            # Fetch reviews using SQLAlchemy ORM
            reviews = (
                db.session.query(OrganismRating)
                .filter(OrganismRating.organism_id == organism_id)
                .order_by(OrganismRating.created_at.desc())
                .all()
            )

            # Serialize reviews
            reviews_list = []
            for review in reviews:
                reviews_list.append({
                    'id': review.id,
                    'organism_id': review.organism_id,
                    'rating': review.rating,
                    'review': review.review,
                    'reviewer_name': review.reviewer_name or OrganismService.ANONYMOUS_USER,
                    'reviewer_email': review.reviewer_email or OrganismService.ANONYMOUS_USER,
                    'created_at': review.created_at.isoformat() if review.created_at else None,
                    'updated_at': review.updated_at.isoformat() if review.updated_at else None,
                })

            # Calculate stats
            stats = (
                db.session.query(
                    func.avg(OrganismRating.rating).label('average_rating'),
                    func.count(OrganismRating.id).label('review_count')
                )
                .filter(OrganismRating.organism_id == organism_id)
                .first()
            )

            average_rating = float(stats.average_rating) if stats.average_rating else 0
            review_count = stats.review_count if stats.review_count else 0

            return {
                'reviews': reviews_list,
                'average_rating': round(average_rating, 1),
                'review_count': review_count
            }
            
        except Exception as e:
            # current_app.logger.error(f"Error fetching reviews for organism {organism_id}: {str(e)}")
            raise Exception("Failed to fetch reviews") from e

    @staticmethod
    def add_organism_rating(organism_id: int, rating_data: dict):
        """
        Add a new rating for an organism
        
        Args:
            organism_id (int): Organism ID to add rating for
            rating_data (dict): Rating data including rating, review, etc.
            
        Returns:
            int: ID of the newly created rating
            
        Raises:
            ValueError: If validation fails
            Exception: If database operation fails
        """
        try:
            rating = rating_data.get('rating')
            review = rating_data.get('review', '')
            reviewer_name = rating_data.get('user_name', OrganismService.ANONYMOUS_USER)
            reviewer_email = rating_data.get('user_email', OrganismService.ANONYMOUS_USER)

            # Validate rating value
            if not isinstance(rating, int) or rating < OrganismService.MIN_RATING or rating > OrganismService.MAX_RATING:
                raise ValueError(f'Rating must be an integer between {OrganismService.MIN_RATING} and {OrganismService.MAX_RATING}')

            # Validate review length
            if review and len(review) > 1000:
                raise ValueError('Review must be less than 1000 characters')

            # Insert new rating using SQLAlchemy
            new_rating = OrganismRating(
                organism_id=organism_id,
                rating=rating,
                review=review,
                reviewer_name=reviewer_name,
                reviewer_email=reviewer_email,
                created_at=datetime.now(timezone.utc)
            )
            db.session.add(new_rating)
            db.session.commit()

            return new_rating.id
            
        except ValueError:
            # Re-raise validation errors
            raise
        except Exception as e:
            db.session.rollback()
            # current_app.logger.error(f"Error adding rating for organism {organism_id}: {str(e)}")
            raise Exception("Failed to add rating") from e

    @staticmethod
    def validate_stage_id(stage_id: int) -> bool:
        """
        Validate if a clinical stage ID exists
        
        Args:
            stage_id (int): The stage ID to validate
            
        Returns:
            bool: True if stage exists, False otherwise
        """
        try:
            if not isinstance(stage_id, int) or stage_id < 1:
                return False
                
            stage = ClinicalStage.get_by_id(stage_id)
            return stage is not None
            
        except Exception as e:
            # current_app.logger.error(f"Error validating stage ID {stage_id}: {str(e)}")
            return False