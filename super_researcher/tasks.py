from celery import shared_task
import subprocess

@shared_task
def run_super_researcher():
    working_dir = "super_researcher"
    command_to_run_cli = ["adk", "run", "engine"]
    prompt_for_ai = """I am a medical supply company called gosupply. I sell nutricia and avanos products. These brands focus on producing enteral feeding products. Refine a target market for these products and find customers. More specifically for customers I want you to research for customers like aged care hospitals anyone that would otherwise need nutricia and avanos. I would like these organizations details like emails, addresses and phone numbers."""    
    
    try:
        process = subprocess.Popen(
            command_to_run_cli,
            cwd=working_dir,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        print(f"Starting process: {' '.join(command_to_run_cli)}")
        print("Sending the following prompt to the AI...")
        print("--- PROMPT ---")
        print(prompt_for_ai)
        print("---------------\n")
        stdout, stderr = process.communicate(input=prompt_for_ai)
        print("--- AI RESPONSE (STDOUT) ---")
        print(stdout)
        print("\n--- ERRORS (STDERR) ---")
        print(stderr)
        print(f"\nProcess finished with return code: {process.returncode}")
    
    except FileNotFoundError:
        print(f"Error: The command '{command_to_run_cli[0]}' was not found.")
        print("Please ensure 'adk' is installed and in your system's PATH.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


run_super_researcher()