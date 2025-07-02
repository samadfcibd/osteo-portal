from flask import Blueprint, render_template, request, jsonify
from app.db import get_db_connection
import pprint


bp = Blueprint('main', __name__)

@bp.route("/")
def index():
    return render_template("index.html")

@bp.route("/api/clinical-stages")
def get_clinical_stages():

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT *
            FROM clinical_stages
        """
        cursor.execute(query)
        results = cursor.fetchall()

        conn.close()

        # Add the "Select stage" option at the beginning
        select_option = {
            'stage_id': '',
            'stage_name': 'Select stage'
        }
        results.insert(0, select_option)
        
        # Return JSON response
        return jsonify({
            'success': True,
            'data': results
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
        
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()



# @bp.route("/api/organisms")
# def get_organisms():

#     try:

#         stage = request.args.get("stage")
        
#         if not stage:
#             return jsonify({
#                 'success': False,
#                 'message': 'Stage parameter is required'
#             }), 400

#         # Pagination
#         page = request.args.get("page", default=1, type=int)
#         per_page = request.args.get("per_page", default=10, type=int)
#         offset = (page - 1) * per_page

#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)

#         query = """
#             select research_data.*, proteins.protein_name, compounds.compound_name, organisms.organism_name, organisms.organism_type
#             from research_data
#             left join proteins on proteins.protein_id = research_data.protein_id
#             left join compounds on compounds.compound_id = research_data.compound_id
#             left join organisms on organisms.organism_id = research_data.organism_id
#             where stage_id = %s
#         """
#         query += " LIMIT %s OFFSET %s"

#         cursor.execute(query, (stage, per_page, offset))
#         results = cursor.fetchall()


#         # Count total records for pagination info
#         count_query = "SELECT COUNT(*) as total FROM research_data WHERE stage_id = %s"
#         cursor.execute(count_query, (stage,))
#         total = cursor.fetchone()['total']

#         conn.close()
        
#         # Return JSON response
#         return jsonify({
#             'success': True,
#             'data': results,
#             'pagination': {
#                 'total': total,
#                 'page': page,
#                 'per_page': per_page,
#                 'total_pages': (total + per_page - 1) // per_page
#             }
#         })
#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'message': str(e)
#         }), 500
        
#     finally:
#         if 'conn' in locals() and conn.is_connected():
#             conn.close()


@bp.route("/api/organisms")
def get_organisms():
    try:
        stage = request.args.get("stage")
        
        if not stage:
            return jsonify({
                'success': False,
                'message': 'Stage parameter is required'
            }), 400

        # Pagination
        page = request.args.get("page", default=1, type=int)
        per_page = request.args.get("per_page", default=10, type=int)
        offset = (page - 1) * per_page

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Main query with LEFT JOIN to get ratings
        query = """
            SELECT 
                rd.*, 
                p.protein_name, 
                c.compound_name, 
                o.organism_name, 
                o.organism_type,
                COALESCE(ROUND(AVG(ort.rating), 1), NULL) as average_rating,
                COUNT(ort.id) as review_count,
                COUNT(CASE WHEN ort.review IS NOT NULL AND ort.review != '' THEN 1 END) as reviews_with_text
            FROM research_data rd
            LEFT JOIN proteins p ON p.protein_id = rd.protein_id
            LEFT JOIN compounds c ON c.compound_id = rd.compound_id
            LEFT JOIN organisms o ON o.organism_id = rd.organism_id
            LEFT JOIN organism_ratings ort ON ort.organism_id = o.organism_id
            WHERE rd.stage_id = %s
            GROUP BY rd.data_id, o.organism_name
            LIMIT %s OFFSET %s
        """
        cursor.execute(query, (stage, per_page, offset))
        results = cursor.fetchall()

        # Count total records (modified to match the same filtering)
        count_query = """
            SELECT COUNT(*) as total 
            FROM research_data rd
            WHERE rd.stage_id = %s
        """
        cursor.execute(count_query, (stage,))
        total = cursor.fetchone()['total']

        conn.close()
        
        # Format the response with proper null handling
        formatted_results = []
        for row in results:
            formatted_row = {
                **row,
                'rating': {
                    'average_rating': float(row['average_rating']) if row['average_rating'] is not None else None,
                    'review_count': row['review_count'],
                    'reviews_with_text': row['reviews_with_text']
                } if row['review_count'] > 0 else None
            }
            formatted_results.append(formatted_row)
        
        return jsonify({
            'success': True,
            'data': formatted_results,
            'pagination': {
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': (total + per_page - 1) // per_page
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
        
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()


# @bp.route("/api/organisms/<int:organism_id>/rating")
# def get_organism_rating(organism_id):
#     """Get average rating and review count for a specific organism"""
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)

#         query = """
#             SELECT 
#                 ROUND(AVG(rating), 1) as average_rating,
#                 COUNT(*) as review_count,
#                 COUNT(CASE WHEN review IS NOT NULL AND review != '' THEN 1 END) as reviews_with_text
#             FROM organism_ratings 
#             WHERE organism_id = %s
#         """
#         cursor.execute(query, (organism_id,))
#         result = cursor.fetchone()

#         conn.close()

#         # If no ratings found, return null values
#         if result['review_count'] == 0:
#             rating_data = {
#                 'average_rating': None,
#                 'review_count': 0,
#                 'reviews_with_text': 0
#             }
#         else:
#             rating_data = result

#         return jsonify({
#             'success': True,
#             'rating': rating_data
#         })

#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'message': str(e)
#         }), 500
        
#     finally:
#         if 'conn' in locals() and conn.is_connected():
#             conn.close()


@bp.route("/api/organisms/<int:organism_id>/ratings")
def get_organism_ratings_detailed(organism_id):
    """Get detailed ratings and reviews for a specific organism"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        offset = (page - 1) * per_page

        # Get total count
        count_query = """
            SELECT COUNT(*) as total
            FROM organism_ratings 
            WHERE organism_id = %s
        """
        cursor.execute(count_query, (organism_id,))
        total_count = cursor.fetchone()['total']

        # Get detailed ratings with pagination (without user info)
        query = """
            SELECT 
                r.id,
                r.rating,
                r.review,
                r.reviewer_name,
                r.created_at
            FROM organism_ratings r
            WHERE r.organism_id = %s
            ORDER BY r.created_at DESC
            LIMIT %s OFFSET %s
        """
        cursor.execute(query, (organism_id, per_page, offset))
        ratings = cursor.fetchall()

        # Get summary statistics
        summary_query = """
            SELECT 
                ROUND(AVG(rating), 1) as average_rating,
                COUNT(*) as total_ratings,
                SUM(CASE WHEN rating = 5 THEN 1 ELSE 0 END) as five_star,
                SUM(CASE WHEN rating = 4 THEN 1 ELSE 0 END) as four_star,
                SUM(CASE WHEN rating = 3 THEN 1 ELSE 0 END) as three_star,
                SUM(CASE WHEN rating = 2 THEN 1 ELSE 0 END) as two_star,
                SUM(CASE WHEN rating = 1 THEN 1 ELSE 0 END) as one_star
            FROM organism_ratings 
            WHERE organism_id = %s
        """
        cursor.execute(summary_query, (organism_id,))
        summary = cursor.fetchone()

        conn.close()

        return jsonify({
            'success': True,
            'data': ratings,
            'summary': summary,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total_count,
                'total_pages': (total_count + per_page - 1) // per_page
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
        
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()


@bp.route("/api/organisms/<int:organism_id>/rating", methods=['POST'])
def add_organism_rating(organism_id):
    """Add a new rating for an organism (anonymous rating)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'rating' not in data:
            return jsonify({
                'success': False,
                'message': 'Rating is required'
            }), 400

        rating = data.get('rating')
        review = data.get('review', '')
        reviewer_name = data.get('user_name', 'Anonymous')  # Optional name field
        reviewer_email = data.get('user_email', 'Anonymous')  # Optional email field

        # Validate rating value
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            return jsonify({
                'success': False,
                'message': 'Rating must be an integer between 1 and 5'
            }), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert new rating (no duplicate check since no user system)
        insert_query = """
            INSERT INTO organism_ratings (organism_id, rating, review, reviewer_name, reviewer_email, created_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """
        cursor.execute(insert_query, (organism_id, rating, review, reviewer_name, reviewer_email))

        conn.commit()
        rating_id = cursor.lastrowid
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Rating added successfully',
            'rating_id': rating_id
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
        
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()



@bp.route("/api/organisms/<int:organism_id>/reviews")
def get_organism_reviews(organism_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT 
                id, organism_id, rating, review,
                COALESCE(reviewer_name, 'Anonymous') as reviewer_name,
                COALESCE(reviewer_email, 'Anonymous') as reviewer_email,
                created_at, updated_at
            FROM organism_ratings
            WHERE organism_id = %s
            ORDER BY created_at DESC
        """
        cursor.execute(query, (organism_id,))
        reviews = cursor.fetchall() or []  # Ensure empty array if None
        
        stats_query = """
            SELECT 
                AVG(rating) as average_rating,
                COUNT(*) as review_count
            FROM organism_ratings
            WHERE organism_id = %s
        """
        cursor.execute(stats_query, (organism_id,))
        stats = cursor.fetchone() or {'average_rating': None, 'review_count': 0}

        return jsonify({
            'success': True,
            'data': {
                'reviews': reviews,  # Guaranteed to be a list
                'average_rating': float(stats['average_rating']) if stats['average_rating'] else 0,
                'review_count': stats['review_count']
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e),
            'data': {  # Return consistent structure even on error
                'reviews': [],
                'average_rating': 0,
                'review_count': 0
            }
        }), 500

    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()