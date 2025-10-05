"""
Organism Upload Service
Handles business logic for importing research data from CSV files
"""

import pandas as pd
from sqlalchemy import text
from api.db import db


class OrganismUploadService:
    """Service class for organism upload operations"""
    
    @staticmethod
    def validate_csv_file(csv_file):
        """
        Validate uploaded CSV file
        
        Args:
            csv_file: Flask file object
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not csv_file or csv_file.filename == '':
            return False, "No file selected"
            
        if not csv_file.filename.lower().endswith('.csv'):
            return False, "File must be a CSV"
            
        return True, ""

    @staticmethod
    def read_csv_data(csv_file):
        """
        Read and validate CSV data
        
        Args:
            csv_file: Flask file object
            
        Returns:
            pandas.DataFrame: CSV data
            
        Raises:
            ValueError: If CSV reading fails or required columns are missing
        """
        try:
            df = pd.read_csv(csv_file)
            
            # Validate required columns
            required_columns = ['Target', 'compound_name', 'iupac_name', 'organisms', 'clinical_stage']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
                
            return df
            
        except Exception as e:
            raise ValueError(f"Failed to read CSV file: {str(e)}")

    @staticmethod
    def import_research_data(df):
        """
        Import research data from DataFrame into database
        
        Args:
            df (pandas.DataFrame): Data to import
            
        Returns:
            dict: Import results
            
        Raises:
            Exception: If import fails
        """
        try:
            # Process data in transaction
            with db.engine.begin() as connection:
                # Step 1: Process proteins
                protein_stats = OrganismUploadService._import_proteins(connection, df)
                
                # Step 2: Process compounds
                compound_stats = OrganismUploadService._import_compounds(connection, df)
                
                # Step 3: Process organisms
                organism_stats = OrganismUploadService._import_organisms(connection, df)
                
                # Step 4: Process research_data
                research_data_stats = OrganismUploadService._import_research_data(connection, df)
            
            return {
                'success': True,
                'message': 'Data imported successfully',
                'stats': {
                    'proteins': protein_stats,
                    'compounds': compound_stats,
                    'organisms': organism_stats,
                    'research_data': research_data_stats
                }
            }
            
        except Exception as e:
            # current_app.logger.error(f"CSV import failed: {str(e)}")
            raise Exception(f"Import failed: {str(e)}")

    @staticmethod
    def _import_proteins(connection, df):
        """Import proteins from DataFrame"""
        proteins = df['Target'].unique()
        
        # Get existing proteins
        existing_proteins = connection.execute(
            text("SELECT protein_name FROM proteins WHERE protein_name IN :proteins"),
            {"proteins": tuple(proteins)}
        ).fetchall()
        
        existing_proteins_set = {row[0] for row in existing_proteins}
        
        # Insert only new proteins
        new_proteins = [p for p in proteins if p not in existing_proteins_set]
        
        for protein in new_proteins:
            connection.execute(
                text("INSERT INTO proteins (protein_name) VALUES (:protein)"),
                {"protein": protein}
            )

        return {
            'total_found': len(proteins),
            'existing': len(existing_proteins_set),
            'imported': len(new_proteins)
        }

    @staticmethod
    def _import_compounds(connection, df):
        """Import compounds from DataFrame"""
        compound_names = df['compound_name'].unique()
        
        # Get existing compounds
        existing_compounds = connection.execute(
            text("SELECT compound_name FROM compounds WHERE compound_name IN :names"),
            {"names": tuple(compound_names)}
        ).fetchall()
        
        existing_compounds_set = {row[0] for row in existing_compounds}
        
        # Insert only new compounds
        imported_count = 0
        processed_compounds = set()
        
        for _, row in df.iterrows():
            compound_name = row['compound_name']
            
            if (compound_name not in existing_compounds_set and 
                compound_name not in processed_compounds):
                
                connection.execute(
                    text("""INSERT INTO compounds 
                        (compound_name, compound_IUPAC) 
                        VALUES (:name, :iupac)"""),
                    {"name": compound_name, "iupac": row['iupac_name']}
                )
                processed_compounds.add(compound_name)
                imported_count += 1

        return {
            'total_found': len(compound_names),
            'existing': len(existing_compounds_set),
            'imported': imported_count
        }

    @staticmethod
    def _import_organisms(connection, df):
        """Import organisms from DataFrame"""
        all_organisms = []
        
        # Collect all unique organisms from the dataframe
        for _, row in df.iterrows():
            organism_value = row['organisms']
            
            if pd.isna(organism_value) or organism_value == '':
                continue
                
            organisms = str(organism_value).split('|')
            for organism in organisms:
                organism = organism.strip()
                if organism:
                    all_organisms.append(organism)
        
        unique_organisms = list(set(all_organisms))
        
        if not unique_organisms:
            return {
                'total_found': 0,
                'existing': 0,
                'imported': 0
            }
        
        # Get existing organisms
        placeholders = ', '.join(['%s'] * len(unique_organisms))
        query = f"SELECT organism_name FROM organisms WHERE organism_name IN ({placeholders})"
        
        existing_organisms = connection.execute(
            query,
            tuple(unique_organisms)
        ).fetchall()
        
        existing_organisms_set = {row[0] for row in existing_organisms}
        
        # Insert only new organisms
        new_organisms = [org for org in unique_organisms if org not in existing_organisms_set]
        
        for organism in new_organisms:
            connection.execute(
                text("""INSERT INTO organisms 
                    (organism_name, organism_type) 
                    VALUES (:name, :type)"""),
                {"name": organism, "type": 'natural'}
            )

        return {
            'total_found': len(unique_organisms),
            'existing': len(existing_organisms_set),
            'imported': len(new_organisms)
        }

    @staticmethod
    def _import_research_data(connection, df):
        """Import research data from DataFrame"""
        combinations_to_check = []
        combinations_data = []
        
        for index, row in df.iterrows():
            # Get protein_id
            protein_result = connection.execute(
                text("SELECT protein_id FROM proteins WHERE protein_name = :name"),
                {"name": row['Target']}
            )
            protein_id = protein_result.scalar()
            if not protein_id:
                continue
            
            # Get compound_id
            compound_result = connection.execute(
                text("SELECT compound_id FROM compounds WHERE compound_name = :name"),
                {"name": row['compound_name']}
            )
            compound_id = compound_result.scalar()
            if not compound_id:
                continue
            
            # Process organisms and stages
            organisms = [org.strip() for org in str(row['organisms']).split('|') if org.strip()]
            stages = [s.strip() for s in str(row['clinical_stage']).split(',') if s.strip()]
            
            for organism in organisms:
                organism_result = connection.execute(
                    text("SELECT organism_id FROM organisms WHERE organism_name = :name"),
                    {"name": organism}
                )
                organism_id = organism_result.scalar()
                if not organism_id:
                    continue
                
                for stage in stages:
                    try:
                        stage_int = int(stage)
                        combinations_to_check.append((protein_id, compound_id, organism_id, stage_int, 1))
                        combinations_data.append((protein_id, compound_id, organism_id, stage_int, 1, index))
                    except ValueError:
                        # Log invalid stage values
                        # current_app.logger.warning(f"Invalid stage value: {stage}")
                        pass
        
        if not combinations_to_check:
            return {
                'total_processed': 0,
                'existing': 0,
                'imported': 0
            }
        
        # Check which combinations already exist
        existing_combinations = set()
        batch_size = 100
        
        for i in range(0, len(combinations_to_check), batch_size):
            batch = combinations_to_check[i:i + batch_size]
            
            # Build query to check existing combinations
            placeholders = ', '.join(['(%s, %s, %s, %s, %s)'] * len(batch))
            params = []
            for combo in batch:
                params.extend(combo)
            
            existing_results = connection.execute(
                f"""SELECT protein_id, compound_id, organism_id, stage_id, country_id 
                FROM research_data 
                WHERE (protein_id, compound_id, organism_id, stage_id, country_id) IN ({placeholders})""",
                params
            ).fetchall()
            
            existing_combinations.update(existing_results)
        
        # Insert only non-existing combinations
        imported_count = 0
        for combo_data in combinations_data:
            protein_id, compound_id, organism_id, stage_int, country_id, index = combo_data
            combo_tuple = (protein_id, compound_id, organism_id, stage_int, country_id)
            
            if combo_tuple not in existing_combinations:
                connection.execute(
                    text("""INSERT INTO research_data 
                        (protein_id, compound_id, organism_id, stage_id, country_id) 
                        VALUES (:protein_id, :compound_id, :organism_id, :stage_id, :country_id)"""),
                    {
                        "protein_id": protein_id,
                        "compound_id": compound_id, 
                        "organism_id": organism_id,
                        "stage_id": stage_int,
                        "country_id": country_id
                    }
                )
                imported_count += 1

        return {
            'total_processed': len(combinations_data),
            'existing': len(existing_combinations),
            'imported': imported_count
        }