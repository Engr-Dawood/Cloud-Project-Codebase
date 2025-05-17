import json
import boto3
import csv
import datetime
import os
from tabulate import tabulate

# Initialize Bedrock client
bedrock = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')
MODEL_ID = 'anthropic.claude-3-haiku-20240307-v1:0'

# Test scenarios
test_scenarios = [
    {
        "name": "Business Partnership",
        "purpose": "Proposing a business partnership",
        "recipient": "CEO of a technology company",
        "key_points": "Our companies have complementary products; Suggest an initial meeting to discuss collaboration; Highlight potential market benefits of partnership",
        "tone": "professional but enthusiastic"
    },
    {
        "name": "Job Interview Follow-up",
        "purpose": "Following up after a job interview",
        "recipient": "HR Manager",
        "key_points": "Express gratitude for the interview opportunity; Reiterate interest in the position; Mention specific discussion point from interview; Ask about next steps in the process",
        "tone": "professional and appreciative"
    },
    {
        "name": "Customer Complaint",
        "purpose": "Addressing a customer complaint",
        "recipient": "Upset customer",
        "key_points": "Apologize for the inconvenience; Explain what happened; Offer a solution or compensation; Assure it won't happen again",
        "tone": "apologetic and helpful"
    },
    {
        "name": "Project Update",
        "purpose": "Providing project status update",
        "recipient": "Project stakeholders",
        "key_points": "Current project status; Milestones achieved; Challenges encountered; Next steps and timeline",
        "tone": "professional and informative"
    }
]

def generate_email(scenario):
    """Generate email using Amazon Bedrock"""
    
    # Prepare the prompt
    prompt = f"""
    You are a professional email assistant. Draft a professional email with the following details:

    Purpose: {scenario['purpose']}
    Recipient: {scenario['recipient']}
    Key points: {scenario['key_points']}
    Tone: {scenario['tone']}

    Format the email with an appropriate subject line, greeting, body, and closing.
    """
    
    # Prepare request body for Claude model
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "temperature": 0.7,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        # Invoke the model
        response = bedrock.invoke_model(
            modelId=MODEL_ID,
            body=json.dumps(request_body)
        )
        
        # Parse the response
        response_body = json.loads(response['body'].read().decode('utf-8'))
        generated_email = response_body['content'][0]['text']
        
        return generated_email
    except Exception as e:
        print(f"Error generating email: {str(e)}")
        return None

def evaluate_email(email_text, scenario):
    """Use the model to evaluate an email based on criteria"""
    
    evaluation_prompt = f"""
    Please evaluate this email based on the following criteria. Rate each criterion from 1-5 (5 being excellent) and provide brief notes:

    EMAIL:
    {email_text}

    ORIGINAL REQUIREMENTS:
    Purpose: {scenario['purpose']}
    Recipient: {scenario['recipient']}
    Key points to include: {scenario['key_points']}
    Tone: {scenario['tone']}

    CRITERIA TO EVALUATE:
    1. Content Relevance: Does the generated email address the specified purpose?
    2. Professionalism: Is the language and structure appropriate for professional communication?
    3. Tone Consistency: Does the email maintain the requested tone throughout?
    4. Completeness: Does it include all key points mentioned in the input?
    5. Format Correctness: Does it have proper subject, greeting, body, and closing?

    For each criterion, provide a score (1-5) and brief notes. Then provide an overall score and summary evaluation.
    Format your response as a JSON object with the following structure:
    {
        "content_relevance": {"score": X, "notes": "..."},
        "professionalism": {"score": X, "notes": "..."},
        "tone_consistency": {"score": X, "notes": "..."},
        "completeness": {"score": X, "notes": "..."},
        "format_correctness": {"score": X, "notes": "..."},
        "overall": {"score": X, "notes": "..."}
    }
    """
    
    # Prepare request body for evaluation
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "temperature": 0.2,
        "messages": [
            {"role": "user", "content": evaluation_prompt}
        ]
    }
    
    try:
        # Invoke the model for evaluation
        response = bedrock.invoke_model(
            modelId=MODEL_ID,
            body=json.dumps(request_body)
        )
        
        # Parse the response
        response_body = json.loads(response['body'].read().decode('utf-8'))
        evaluation_text = response_body['content'][0]['text']
        
        # Extract the JSON part
        try:
            # Try to find and parse the JSON object in the response
            start_idx = evaluation_text.find('{')
            end_idx = evaluation_text.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = evaluation_text[start_idx:end_idx]
                evaluation = json.loads(json_str)
                return evaluation
            else:
                print("Couldn't find JSON object in response")
                return None
        except json.JSONDecodeError:
            print("Failed to parse evaluation JSON")
            return None
    except Exception as e:
        print(f"Error in evaluation: {str(e)}")
        return None

def analyze_bias_and_ethics(email_text):
    """Analyze the email for potential bias and ethical concerns"""
    
    analysis_prompt = f"""
    Please analyze this email for potential bias and ethical concerns:

    EMAIL:
    {email_text}

    Provide an analysis covering:
    1. Language Bias: Is there any gender, cultural, age, or other bias in the language?
    2. Inclusivity: Is the language inclusive and accessible to diverse audiences?
    3. Ethical Concerns: Are there any ethical issues with the content or approach?
    4. Recommendations: What changes would improve the email from a responsible AI perspective?

    Format your response as a JSON object with the following structure:
    {
        "language_bias": "...",
        "inclusivity": "...",
        "ethical_concerns": "...",
        "recommendations": "..."
    }
    """
    
    # Prepare request body for analysis
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "temperature": 0.2,
        "messages": [
            {"role": "user", "content": analysis_prompt}
        ]
    }
    
    try:
        # Invoke the model for analysis
        response = bedrock.invoke_model(
            modelId=MODEL_ID,
            body=json.dumps(request_body)
        )
        
        # Parse the response
        response_body = json.loads(response['body'].read().decode('utf-8'))
        analysis_text = response_body['content'][0]['text']
        
        # Extract the JSON part
        try:
            start_idx = analysis_text.find('{')
            end_idx = analysis_text.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = analysis_text[start_idx:end_idx]
                analysis = json.loads(json_str)
                return analysis
            else:
                print("Couldn't find JSON object in analysis response")
                return None
        except json.JSONDecodeError:
            print("Failed to parse analysis JSON")
            return None
    except Exception as e:
        print(f"Error in analysis: {str(e)}")
        return None

def run_evaluation():
    """Run the complete evaluation process for all scenarios"""
    
    results = []
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_dir = "evaluation_reports"
    
    # Create directory if it doesn't exist
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)
    
    for scenario in test_scenarios:
        print(f"\nEvaluating scenario: {scenario['name']}...")
        
        # Generate email
        email = generate_email(scenario)
        if not email:
            print("Failed to generate email. Skipping scenario.")
            continue
        
        # Evaluate the email
        evaluation = evaluate_email(email, scenario)
        if not evaluation:
            print("Failed to evaluate email. Skipping further analysis.")
            continue
        
        # Analyze for bias and ethics
        analysis = analyze_bias_and_ethics(email)
        
        # Store results
        result = {
            "scenario": scenario,
            "email": email,
            "evaluation": evaluation,
            "analysis": analysis
        }
        results.append(result)
        
        # Display summary
        print(f"\nScenario: {scenario['name']}")
        print("\nEvaluation Scores:")
        table_data = []
        for criterion, data in evaluation.items():
            if criterion != "overall":
                table_data.append([criterion.replace("_", " ").title(), data["score"], data["notes"]])
        table_data.append(["Overall", evaluation["overall"]["score"], evaluation["overall"]["notes"]])
        print(tabulate(table_data, headers=["Criterion", "Score", "Notes"], tablefmt="grid"))
        
        if analysis:
            print("\nEthical Analysis Summary:")
            print(f"- Language Bias: {analysis['language_bias'][:100]}...")
            print(f"- Recommendations: {analysis['recommendations'][:100]}...")
    
    # Save detailed results to file
    report_file = f"{report_dir}/evaluation_report_{timestamp}.json"
    with open(report_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nDetailed evaluation report saved to {report_file}")
    
    # Generate CSV summary
    csv_file = f"{report_dir}/evaluation_summary_{timestamp}.csv"
    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        headers = ["Scenario", "Content Relevance", "Professionalism", "Tone Consistency", 
                   "Completeness", "Format Correctness", "Overall"]
        writer.writerow(headers)
        
        for result in results:
            row = [
                result["scenario"]["name"],
                result["evaluation"]["content_relevance"]["score"],
                result["evaluation"]["professionalism"]["score"],
                result["evaluation"]["tone_consistency"]["score"],
                result["evaluation"]["completeness"]["score"],
                result["evaluation"]["format_correctness"]["score"],
                result["evaluation"]["overall"]["score"]
            ]
            writer.writerow(row)
    
    print(f"Evaluation summary saved to {csv_file}")

if __name__ == "__main__":
    run_evaluation()
