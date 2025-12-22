import subprocess
import re
from .models import SuperResearcher # Make sure to import your model
from celery import shared_task
from core.celery import app

@shared_task(bind=True)
def run_researcher(self, prompt: str, working_dir: str = "super_researcher"):
    """
    Executes the 'adk' CLI tool with a given prompt and returns its output.

    Args:
        prompt (str): The prompt to send to the AI engine.
        working_dir (str): The directory where the command should be run.

    Returns:
        dict: Result with stdout, stderr, return_code, and task_id.
    """
    command_to_run_cli = ["adk", "run", "engine"]

    try:
        # Update task state to show it's running
        self.update_state(state='PROGRESS', meta={'status': 'Starting researcher process'})

        process = subprocess.Popen(
            command_to_run_cli,
            cwd=working_dir,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        print(f"Starting researcher process: {' '.join(command_to_run_cli)}")
        stdout, stderr = process.communicate(input=prompt)
        return_code = process.returncode

        print(f"Process finished with return code: {return_code}")

        # If successful, trigger the save task
        if return_code == 0 and stdout:
            save_research_output.delay(stdout)

        return {
            'stdout': stdout,
            'stderr': stderr,
            'return_code': return_code,
            'task_id': self.request.id
        }

    except FileNotFoundError:
        error_msg = f"Error: The command '{command_to_run_cli[0]}' was not found."
        print(error_msg + "Please ensure 'adk' is installed and in your system's PATH.")
        return {'stdout': None, 'stderr': error_msg, 'return_code': -1, 'task_id': self.request.id}
    except Exception as e:
        error_msg = f"An unexpected error occurred during subprocess execution: {e}"
        print(error_msg)
        return {'stdout': None, 'stderr': error_msg, 'return_code': -1, 'task_id': self.request.id}
    

@shared_task
def save_research_output(raw_output_text: str):
    """
    Parses the raw text output from the researcher and saves valid leads to the database.

    Args:
        raw_output_text (str): The complete stdout string from the researcher.

    Returns:
        dict: A summary of the operation, e.g., {'found': 5, 'saved': 4}.
    """
    if not raw_output_text:
        print("No output provided to save.")
        return {'found': 0, 'saved': 0}

    leads_saved_count = 0
    leads_found_count = 0
    
    # We assume each lead is separated by at least two newlines.
    # This may need adjustment based on your LLM's actual output format.
    potential_leads = raw_output_text.strip().split('\n\n')

    for lead_block in potential_leads:
        if not lead_block.strip():
            continue

        lead_data = {}
        # Use regex to find "Key: Value" pairs in each block.
        # This is robust and handles keys with spaces.
        matches = re.findall(r'^(.+?):\s*(.+)$', lead_block.strip(), re.MULTILINE)

        for key, value in matches:
            clean_key = key.strip().lower()
            clean_value = value.strip()
            
            # --- Map the LLM's output keys to your Django model fields ---
            if 'company' in clean_key:
                lead_data['company'] = clean_value
            elif 'website' in clean_key:
                lead_data['website'] = clean_value
            elif 'phone' in clean_key:
                lead_data['phone_number'] = clean_value
            elif 'email' in clean_key:
                lead_data['email'] = clean_value
            elif 'address' in clean_key:
                lead_data['address'] = clean_value
            elif 'contact' in clean_key or 'name' in clean_key:
                lead_data['full_name'] = clean_value
        
        # Only attempt to save if we found a key piece of information like a company name.
        if 'company' in lead_data:
            leads_found_count += 1
            try:
                SuperResearcher.objects.create(
                    company=lead_data.get('company'),
                    website=lead_data.get('website'),
                    phone_number=lead_data.get('phone_number'),
                    email=lead_data.get('email'),
                    address=lead_data.get('address'),
                    full_name=lead_data.get('full_name'),
                    lead_class='New' # Default classification
                )
                leads_saved_count += 1
                print(f"Successfully saved lead: {lead_data.get('company')}")

            except Exception as e:
                # This catches database errors, like invalid email format, etc.
                print(f"Failed to save lead for '{lead_data.get('company')}'. Error: {e}")

    summary = {
        'found': leads_found_count,
        'saved': leads_saved_count
    }
    print(f"\n--- DATABASE SAVE SUMMARY ---")
    print(f"Found {summary['found']} potential leads.")
    print(f"Successfully saved {summary['saved']} leads to the database.")
    print("-----------------------------\n")
    
    return summary