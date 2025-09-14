from google import genai
from pydantic import BaseModel

class DocumentationOutput(BaseModel):
    title: str
    description: str
    method: str
    endpointURL: str
    frontendCodeSample: str
    JSONSample: str


def generateDocumentation(code: str, documentationLanguage: str, sampleCodingLanguage: str):
    try:
        client = genai.Client()
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Given this Code{code}, return technical documentation in this code language {sampleCodingLanguage}, in this language {documentationLanguage}",
            config={
                "response_mime_type": "application/json",
                "response_schema": list[DocumentationOutput]
            }
        )
        return { "message": "Successfully Generated Documentation", "success": True, "data": response}
    except Exception as e:
        return { "message": "Internal Server Error", "success": False}