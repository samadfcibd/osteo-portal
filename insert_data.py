import pandas as pd
import mysql.connector

# ========== CONFIGURATION ==========
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "p4pKsEh106"
DB_NAME = "osteoarthritis_db"    # use osteoarthritis_test first for testing
DB_PORT = 3305
CSV_FILE = "Input_Data.csv"
# ==================================

def main():
    # Connect to database
    conn = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME,
    port=DB_PORT
    )
    cursor = conn.cursor()

    # Counters for logging
    log = {
        "proteins_new": 0, "proteins_existing": 0,
        "compounds_new": 0, "compounds_existing": 0,
        "organisms_new": 0, "organisms_existing": 0,
        "research_links": 0
    }

    # Load Excel
    df = pd.read_csv(CSV_FILE)

    for _, row in df.iterrows():
        # Insert protein
        cursor.execute("""
            INSERT INTO proteins (protein_name) VALUES (%s)
            ON DUPLICATE KEY UPDATE protein_id=LAST_INSERT_ID(protein_id)
        """, (row['protein_name'],))
        protein_id = cursor.lastrowid
        log["proteins_new" if cursor.rowcount == 1 else "proteins_existing"] += 1

        # Insert compound
        cursor.execute("""
            INSERT INTO compounds (compound_name, compound_IUPAC)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE compound_id=LAST_INSERT_ID(compound_id),
                                    compound_IUPAC=VALUES(compound_IUPAC)
        """, (row['compound_name'], row['compound_IUPAC']))
        compound_id = cursor.lastrowid
        log["compounds_new" if cursor.rowcount == 1 else "compounds_existing"] += 1

        # Insert organisms (may be multiple separated by "|")
        organisms = str(row['organism_type']).split("|")
        for org in organisms:
            org = org.strip()
            if not org:
                continue
            cursor.execute("""
                INSERT INTO organisms (organism_name) VALUES (%s)
                ON DUPLICATE KEY UPDATE organism_id=LAST_INSERT_ID(organism_id)
            """, (org,))
            organism_id = cursor.lastrowid
            log["organisms_new" if cursor.rowcount == 1 else "organisms_existing"] += 1

            # Insert into research_data for each stage_id
            stage_ids = [int(s.strip()) for s in str(row['stage_id']).split(",") if s.strip().isdigit()]
            for stage_id in stage_ids:
                cursor.execute("""
                    INSERT INTO research_data (protein_id, stage_id, compound_id, organism_id, country_id)
                    VALUES (%s, %s, %s, %s, 1)
                    ON DUPLICATE KEY UPDATE data_id=data_id
                  """, (protein_id, stage_id, compound_id, organism_id))
                log["research_links"] += 1

        print(f"Processed: {row['protein_name']} | stage_ids={row['stage_id']} | compound={row['compound_name']}")

    # Commit changes
    conn.commit()
    cursor.close()
    conn.close()

    # Print log summary
    print("\n===== UPLOAD SUMMARY =====")
    for k, v in log.items():
        print(f"{k}: {v}")
    print("==========================")

if __name__ == "__main__":
    main()
