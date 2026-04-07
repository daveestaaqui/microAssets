import os
import io
from PIL import Image
try:
    from google import genai
    from google.genai import types

    client = genai.Client() # Assumes GEMINI_API_KEY is in env
    
    result = client.models.generate_images(
        model='imagen-3.0-generate-002',
        prompt='A simple square.',
        config=types.GenerateImagesConfig(
            number_of_images=1,
            output_mime_type="image/png",
            aspect_ratio="1:1"
        )
    )
    for generated_image in result.generated_images:
        image = Image.open(io.BytesIO(generated_image.image.image_bytes))
        image.save('test_genai_output.png')
    print("SUCCESS")
except Exception as e:
    print("FAILED:", e)
