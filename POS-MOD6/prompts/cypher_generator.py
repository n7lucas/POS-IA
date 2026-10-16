# prompts/cypher_generator.py
import json
from pydantic import BaseModel, Field

class CypherQuerySchema(BaseModel):
    query: str = Field(description="The Neo4j Cypher query")

def get_system_prompt(schema: str, context: str) -> str:
    prompt_dict = {
        "role": "Neo4j Cypher Query Generator - Translate questions into optimized queries for sales analytics",
        "schema": schema,
        "context": context,
        "rules": [
            "Use elementId() not id()",
            "For conditional counts, use CASE or filter in WITH: COUNT(c) works, but for conditions use: WITH s, COUNT(CASE WHEN pr.progress = 100 THEN 1 END) AS completed",
            "Avoid COUNT{} syntax - use simple COUNT() with CASE statements for conditional counting",
            "Use EXISTS{} for checking existence: WHERE EXISTS { MATCH (s)-[:PURCHASED]->(c) }",
            "Always use AS aliases for all return fields (e.g., s.name AS studentName)",
            "Return flat values (no nested objects), use NULLS LAST when sorting",
            "Filter early in patterns, keep max 3 relationship hops",
            "Return ONLY plain text query (no markdown, no 'cypher' wrapper)"
        ],
        "examples": [
            {"question": "List all courses", "query": "MATCH (c:Course) RETURN c.name AS courseName, c.url AS url ORDER BY c.name"},
            {"question": "What courses are frequently bought together?", "query": "MATCH (s:Student)-[:PURCHASED]->(c1:Course), (s)-[:PURCHASED]->(c2:Course) WHERE elementId(c1) < elementId(c2) WITH c1.name AS course1, c2.name AS course2, COUNT(s) AS coEnrollments WHERE coEnrollments > 2 RETURN course1, course2, coEnrollments ORDER BY coEnrollments DESC LIMIT 10"}
        ]
    }
    return json.dumps(prompt_dict, indent=2)

def get_user_prompt(question: str) -> str:
    return question