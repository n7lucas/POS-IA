import json
import random
import asyncio
from faker import Faker
from services.neo4j_service import Neo4jService

# Inicializa o Faker com dados em Português-BR
fake = Faker('pt_BR')

def generate_test_data(courses):
    students = []
    # Cria 20 estudantes
    for _ in range(20):
        students.append({
            "id": fake.uuid4(),
            "name": fake.name(),
            "email": fake.email(),
            "phone": fake.phone_number(),
        })

    sales_records = []
    # Para cada estudante, cria de 1 a 10 vendas
    for student in students:
        num_sales = random.randint(1, 10)
        for _ in range(num_sales):
            sales_records.append({
                "studentId": student["id"],
                "courseId": random.choice(courses)["name"],
                "status": random.choice(["paid", "refunded"]),
                "paymentMethod": random.choice(["pix", "credit_card"]),
                "paymentDate": fake.date_time_this_year().isoformat(),
                "amount": round(random.uniform(0, 2000), 2),
            })

    progress_records = []
    # Para cada curso pago, gera um progresso de 0 a 100
    for sale in sales_records:
        if sale["status"] == "paid":
            progress_records.append({
                "studentId": sale["studentId"],
                "courseId": sale["courseId"],
                "progress": random.randint(0, 100),
            })

    return students, sales_records, progress_records

async def seed_database():
    print("📖 Carregando courses.json...")
    with open("data/courses.json", "r", encoding="utf-8") as f:
        courses = json.load(f)

    neo4j_service = Neo4jService()
    
    # Dependendo de como seu serviço Neo4j está construído, você pode 
    # precisar ajustar esta query de limpeza. O padrão em Cypher é:
    print("🧹 Limpando o banco de dados...")
    await neo4j_service.query("MATCH (n) DETACH DELETE n")
    print("✅ Banco limpo!")

    students, sales_records, progress_records = generate_test_data(courses)

    print("⏳ Inserindo Cursos...")
    await neo4j_service.query(
        """
        UNWIND $batch AS row
        MERGE (c:Course {name: row.name})
        ON CREATE SET c.url = row.url
        """,
        {"batch": courses}
    )
    
    print("⏳ Inserindo Estudantes...")
    await neo4j_service.query(
        """
        UNWIND $batch AS row
        MERGE (s:Student {id: row.id})
        ON CREATE SET s.name = row.name, s.email = row.email, s.phone = row.phone
        """,
        {"batch": students}
    )

    print("⏳ Inserindo Vendas (Relacionamento PURCHASED)...")
    await neo4j_service.query(
        """
        UNWIND $batch AS row
        MATCH (s:Student {id: row.studentId}), (c:Course {name: row.courseId})
        MERGE (s)-[p:PURCHASED]->(c)
        ON CREATE SET p.status = row.status, p.paymentMethod = row.paymentMethod, p.paymentDate = row.paymentDate, p.amount = row.amount
        ON MATCH SET p.status = row.status, p.paymentMethod = row.paymentMethod, p.paymentDate = row.paymentDate, p.amount = row.amount
        """,
        {"batch": sales_records}
    )

    print("⏳ Inserindo Progresso (Relacionamento PROGRESS)...")
    await neo4j_service.query(
        """
        UNWIND $batch AS row
        MATCH (s:Student {id: row.studentId})-[:PURCHASED {status: "paid"}]->(c:Course {name: row.courseId})
        MERGE (s)-[p:PROGRESS]->(c)
        ON CREATE SET p.progress = row.progress
        ON MATCH SET p.progress = row.progress
        """,
        {"batch": progress_records}
    )
    
    print("🎉 Seed concluído com sucesso!")
    # Feche a conexão se o seu serviço possuir um método close()
    if hasattr(neo4j_service, 'close'):
        await neo4j_service.close()

if __name__ == "__main__":
    asyncio.run(seed_database())