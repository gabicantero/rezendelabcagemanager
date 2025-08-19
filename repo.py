from database import get_session
from sqlalchemy import text

def add_animal(animal_data):
    session = get_session()
    query = text("""
        INSERT INTO animals (id, project, cage, dob, sex)
        VALUES (:id, :project, :cage, :dob, :sex)
    """)
    session.execute(query, animal_data)
    session.commit()
    session.close()

def get_animals_by_project(project_name):
    session = get_session()
    query = text("SELECT * FROM animals WHERE project=:project")
    result = session.execute(query, {"project": project_name}).fetchall()
    session.close()
    return result