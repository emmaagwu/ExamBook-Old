# utils.py

# Example utility function
def validate_question_type(question_type):
    allowed_types = ['multiple_choice', 'true_false', 'short_answer']
    return question_type in allowed_types
