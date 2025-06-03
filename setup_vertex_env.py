"""
Script to set up Vertex AI environment variables in .env file.
"""
import os
from pathlib import Path

def setup_vertex_env():
    env_path = Path(__file__).parent / '.env'
    
    # Default Vertex AI configuration
    vertex_config = {
        'VERTEX_AI_PROJECT': 'gen-lang-client-0273830092',
        'VERTEX_AI_LOCATION': 'us-central1',
        'VERTEX_AI_MODEL': 'imagegeneration@002',  # Default model, can be changed as needed
    }
    
    # Check if .env exists and read existing content
    existing_vars = {}
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    existing_vars[key] = value.strip()
    
    # Update with new values, preserving existing ones
    existing_vars.update(vertex_config)
    
    # Write back to .env
    with open(env_path, 'w') as f:
        for key, value in existing_vars.items():
            f.write(f"{key}={value}\n")
    
    print(f"✅ Updated {env_path} with Vertex AI configuration")
    print("\nCurrent configuration:")
    for key, value in vertex_config.items():
        print(f"{key}={value}")
    print("\nNote: If you need to use a different model, please update VERTEX_AI_MODEL in the .env file.")

if __name__ == "__main__":
    setup_vertex_env()
