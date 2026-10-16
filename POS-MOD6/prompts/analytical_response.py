# prompts/analytical_response.py
import json
from pydantic import BaseModel, Field
from typing import List, Dict, Any

class AnalyticalResponseSchema(BaseModel):
    answer: str = Field(description="Complete analytical response in prose format")
    follow_up_questions: List[str] = Field(description="2-3 suggested follow-up questions")

def get_system_prompt() -> str:
    prompt_dict = {
        "role": "Sales Analytics Reporter - Generate data-driven insights in prose",
        "rules": [
            "CRITICAL: Match the QUESTION language, NOT data language. English question = English answer, Portuguese question = Portuguese answer",
            "Write complete analytical responses using actual data (no placeholders)",
            "Include calculations: percentages, distributions, averages, comparisons",
            "Start with key finding, use bullets for lists, highlight patterns",
            "Provide 2-3 specific follow-up questions in the same language as the original question",
            "Do NOT include queries or apologize for errors"
        ],
        "example": {
            "question": "What is the revenue distribution across courses?",
            "dbResults": [{"courseName": "JS Expert", "totalRevenue": 25000}, {"courseName": "Node Streams", "totalRevenue": 15000}],
            "answer": "Strong revenue concentration: **JS Expert** leads with $25,000 (62.5%), **Node Streams** $15,000 (37.5%). Top course generates 67% more than second place, indicating strong market demand.",
            "followUpQuestions": ["Which course has highest completion rate?", "How many students purchased JS Expert?", "What payment methods are most popular?"]
        }
    }
    return json.dumps(prompt_dict, indent=2)

def get_user_prompt(question: str, query: str, db_results: str) -> str:
    return json.dumps({"question": question, "query": query, "dbResults": db_results})

def get_error_prompt(error: str, question: str = "") -> str:
    return json.dumps({
        "error": error, 
        "question": question, 
        "task": "Explain error in user-friendly terms, suggest alternatives, provide 2-3 better questions"
    })

def get_no_results_prompt(question: str, query: str) -> str:
    return json.dumps({
        "question": question, 
        "query": query, 
        "task": "No data found. Suggest reasons and 2-3 alternative questions"
    })

def get_multi_step_prompt(original_question: str, steps: List[Dict[str, Any]]) -> str:
    return json.dumps({
        "original_question": original_question,
        "steps": steps,
        "task": "Synthesize all steps into coherent narrative, highlight comparisons and patterns"
    })