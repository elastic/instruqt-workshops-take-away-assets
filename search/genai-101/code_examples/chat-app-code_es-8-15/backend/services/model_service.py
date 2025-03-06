from .prompt_service import create_prompt


def generate_answer(question, provider='aws_bedrock'):
    results = get_sparse_retriever(question)
    prompt = create_prompt(question, results, index_source_fields)

    if provider == 'aws_bedrock':
        return call_aws_bedrock(prompt)
    # Add more providers as needed


def call_aws_bedrock(prompt):
    # Implement the API call to AWS Bedrock
    pass
