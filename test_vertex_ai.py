"""
Test script for Google Vertex AI Image Generation
"""
import os
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel
from dotenv import load_dotenv

def test_vertex_ai_image_generation():
    # Load environment variables
    load_dotenv()
    
    # Get configuration from environment
    project_id = os.getenv("VERTEX_AI_PROJECT")
    location = os.getenv("VERTEX_AI_LOCATION")
    model_name = os.getenv("VERTEX_AI_MODEL", "imagegeneration@002")
    
    print(f"🚀 Testing Vertex AI Image Generation with model: {model_name}")
    print(f"Project: {project_id}, Location: {location}")
    
    try:
        # Initialize Vertex AI
        vertexai.init(project=project_id, location=location)
        
        # Initialize the model
        model = ImageGenerationModel.from_pretrained(model_name)
        
        # Test prompt
        prompt = "A futuristic city with flying cars and neon lights"
        print(f"\n🤖 Generating image with prompt: '{prompt}'")
        
        # Generate image
        response = model.generate_images(
            prompt=prompt,
            number_of_images=1,
            guidance_scale=7.5,
            aspect_ratio="1:1"
        )
        
        # Save the generated image
        output_file = "test_vertex_output.png"
        response.images[0].save(output_file)
        print(f"✅ Success! Image saved as: {output_file}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Make sure you have run: make gcloud-auth")
        print("2. Verify your Google Cloud project has the Vertex AI API enabled")
        print("3. Check that the service account has the 'Vertex AI User' role")
        print("4. Make sure the model name is correct and available in your region")

if __name__ == "__main__":
    test_vertex_ai_image_generation()
