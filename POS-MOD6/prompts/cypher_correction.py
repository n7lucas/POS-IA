# prompts/cypher_correction.py
import json
from pydantic import BaseModel, Field

class CypherCorrectionSchema(BaseModel):
    corrected_query: str = Field(description="The corrected Neo4j Cypher query")
    explanation: str = Field(description="Brief explanation of what was fixed")

def get_system_prompt(schema: str) -> str:
    prompt_dict = {
        "role": "Neo4j Cypher Query Debugger - Fix invalid queries based on error messages",
        "schema": schema,
        "rules": [
            "Read error carefully, preserve original intent, return valid executable query",
            "Aggregation errors: Use WITH to separate grouping from aggregation",
            "Variable scope errors: Pass variables through WITH or redefine them",
            "NULL errors: Add NULLS LAST/FIRST to ORDER BY",
            "Property errors: Check schema, use correct aliases (n.name AS name)"
        ],
        "example": {
            "failed": "WITH SUM(p.amount) AS total ... RETURN c.name, revenue, round(revenue / total, 2)",
            "error": "Implicit grouping expressions: totalRevenue",
            "corrected": "WITH SUM(p.amount) AS total ... WITH total, c.name AS name, SUM(p2.amount) AS rev RETURN name, rev, round(rev / total, 2)",
            "fix": "Moved grouping into WITH before RETURN"
        }
    }
    return json.dumps(prompt_dict, indent=2)

def get_user_prompt(failed_query: str, error_message: str, original_question: str = "") -> str:
    return json.dumps({
        "failed_query": failed_query,
        "error_message": error_message,
        "original_question": original_question
    })