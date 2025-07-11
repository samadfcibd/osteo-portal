from flask import Blueprint, render_template, request, jsonify, current_app
from app.db import get_db_connection
import pprint

import re
import os
from collections import namedtuple


import requests
from bs4 import BeautifulSoup


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


def load_organism_data():
    """Parse the speclist.txt file and return a dictionary of scientific_name: common_name"""
    organism_data = {}
    # Construct the absolute path to the data file
    data_dir = os.path.join(current_app.root_path, 'app/data')
    file_path = os.path.join(data_dir, 'speclist.txt')

    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if re.match(r'^[A-Z0-9]{4,5} [A-Z]?\s+\d+:.*', line):
                # Check next lines for scientific name (N=) and common name (C=)
                sci_name = None
                common_name = None
                
                for j in range(i+1, min(i+4, len(lines))):
                    next_line = lines[j].strip()
                    if next_line.startswith('N='):
                        sci_name = next_line[2:].strip()
                    elif next_line.startswith('C='):
                        common_name = next_line[2:].strip()
                        break
                
                if sci_name and common_name:
                    organism_data[sci_name.lower()] = common_name
                    i = j
                else:
                    i += 1
            else:
                i += 1
    return organism_data



def get_english_name(scientific_name,  language="English"):
    base_url = "https://sciname.info/Default.asp"
    params = {"SciName": scientific_name}

    response = requests.get(base_url, params=params)
    soup = BeautifulSoup(response.content, "html.parser")

    tables = soup.find_all("table")
    results = []

    for table in tables:
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) >= 2:
                key = cells[0].get_text(strip=True)
                val = cells[1].get_text(strip=True)
                if key.startswith(f"{language}:"):
                    results.append(val)

    return results
    


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
        

        # Load the organism data once at startup
        # organism_lookup = load_organism_data()

        # Format the response with proper null handling
        formatted_results = []
        for row in results:

            # Get the organism name from the row
            organism_name = row['organism_name']
    
            # Look up the common name (case-insensitive)
            common_name = get_english_name(organism_name)
    
            formatted_row = {
                **row,
                'food': common_name,  # Add the common name as 'food'
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