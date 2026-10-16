from pydantic import BaseModel, Field
from typing import List, Literal

class QueryAnalysisSchema(BaseModel):
    complexity: Literal['simple', 'complex'] = Field(description="Where the query is simple or complex")
    requires_decomposition: bool = Field(description="Whether the query need to be broken into sub-queries")
    sub_questions: List[str] = Field(default_factory=list,description="Sub-questions if decomposition is required (empty list if simple)")
    reasoning: str = Field(description="Brief explanation of the analysis")


def get_system_prompt() -> str:
    return """Role: Query Complexity Analyzer - Determine if questions need multi-step decomposition

Rules:
- Generate sub-questions in the SAME language as the input question (ignore data language)
- Simple: Single entity, direct retrieval, no group comparisons
- Complex: Comparing groups, multiple dependent calculations, relationship analysis
- Decompose into max 3 sub-questions, each independently answerable, logically ordered

Examples:
1. 
Question: 'List all available courses'
Analysis: simple, requiresDecomposition: false, subQuestions: [], reasoning: 'Direct retrieval, no comparisons'

2.
Question: 'Compare revenue between high vs low completion courses'
Analysis: complex, requiresDecomposition: true, subQuestions: ['Average completion per course?', 'Revenue for courses >70% completion?', 'Revenue for courses <70% completion?'], reasoning: 'Multiple aggregations + group comparison'
"""

def get_user_prompt(question: str) -> str:
    return question