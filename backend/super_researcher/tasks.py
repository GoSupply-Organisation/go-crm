from pathlib import Path
import subprocess
import json
from .models import SuperResearcher
from celery import shared_task
from .engine.prompting import prompt, structure_prompt
from openai import OpenAI
from decouple import config

@shared_task
def periodic_lead_generation():
    """
    Periodic task that automatically generates AI leads every 5 minutes.
    This task is designed to run without external arguments.
    """
    client = OpenAI(api_key=config("OPENAI_API_KEY"))
    model = "gpt-5-nano"  # Correct model name
    print("Starting periodic AI lead generation...")

    try:
        # Step 1: Run the research task with the default prompt
        research_result = run_researcher(prompt)

        if research_result['return_code'] != 0:
            error_msg = f"Research failed: {research_result['stderr']}"
            print(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'message': 'Research step failed'
            }

        # Step 2: Use GPT to structure the data
        structured_response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": structure_prompt},
                {"role": "user", "content": research_result['stdout']}
            ],
            response_format={"type": "json_object"}
        )

        # Step 3: Parse the JSON response
        lead_data = json.loads(structured_response.choices[0].message.content)

        # Step 4: Save to database
        lead = SuperResearcher.objects.create(
            company=lead_data.get('company'),
            website=lead_data.get('website'),
            phone_number=lead_data.get('phone_number'),
            email=lead_data.get('email'),
            full_name=lead_data.get('full_name'),
            promoted=lead_data.get('promoted', False),
            is_active_lead=lead_data.get('is_active_lead', False),
            lead_class=lead_data.get('lead_class', 'New'),
            notes=lead_data.get('notes'),
            address=lead_data.get('address')
        )

        print(f"Successfully created lead: {lead.company}")
        return {
            'success': True,
            'lead_id': lead.id,
            'company': lead.company,
            'message': 'Lead generated and saved successfully'
        }

    except Exception as e:
        error_msg = f"Failed to start periodic lead generation: {e}"
        print(error_msg)
        return {
            'success': False,
            'error': str(e),
            'message': 'Periodic lead generation failed'
        }


def run_researcher(prompt: str, task_id=None):
    """
    Executes the 'adk' CLI tool with a given prompt.
    """
    working_dir = Path(__file__).resolve().parents[2]
    command_to_run_cli = ["adk", "run", "backend/super_researcher/engine"]
    
    try:
        process = subprocess.Popen(
            command_to_run_cli,
            cwd=working_dir,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Send the prompt and wait for response with a timeout
        try:
            stdout, stderr = process.communicate(input=prompt, timeout=60)
            return_code = process.returncode

            if stderr:
                print("Error output:")
                print(stderr)  # Print full stderr to see what went wrong

            if return_code == 0 and stdout:
                print("Output received:")

            return {
                'stdout': stdout,
                'stderr': stderr,
                'return_code': return_code,
                'task_id': task_id  # Pass this as a parameter instead
            }
        except subprocess.TimeoutExpired:
            print("Process timed out after 60 seconds")
            process.kill()
            stdout, stderr = process.communicate()
            return {
                'stdout': stdout,
                'stderr': stderr,
                'return_code': -2,
                'task_id': task_id
            }

    except FileNotFoundError:
        error_msg = f"Error: 'adk' command was not found."
        print(error_msg)
        return {'stdout': None, 'stderr': error_msg, 'return_code': -1, 'task_id': task_id}


