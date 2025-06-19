from pydantic import BaseModel, Field
from ollama import chat

promt_template = """
    Eres un analizador de mensajes que responde a campañas o contenidos enviados. Tu tarea es procesar cada mensaje y devolver la siguiente información:

    1. Tipo de mensaje:

        - 1: Mensajes que son respuestas preestablecidas en las que se anuncian o presentan los servicios ofrecidos.

        - 0: Mensajes en los que el usuario agradece, pregunta o solicita ayuda de manera personalizada.

    2. Sentimiento (solo para mensajes escritos):

        -2: Si el mensaje expresa agradecimiento, satisfacción u otra intención positiva.

        -1: Si el mensaje muestra quejas, molestia o insatisfacción.

        -0: Si el mensaje es neutral, sin emociones claras.

    3. Ayuda solicitada (solo para mensajes escritos):

        -Identifica qué tipo de asistencia solicita el usuario (por ejemplo, solicitar que un representante se comunique, pedir más información, requerir entradas adicionales para un evento, etc.)

    4. Tipo de ayuda solicitada (solo para mensajes escritos):
        -1: Necesita que alguna persona se comunique con él o ella.

        -0: Necesita ayuda técnica para resolver un problema (por ejemplo, problemas de acceso a una plataforma, no le deja consultar cierta información, etc.)

    El mensaje a analizar es el siguiente:
"""
class Classification(BaseModel):
    Classification: int = Field(description="Tipo de mensaje, 1: respuesta preestablecida, 0: mensaje personalizado")
    Feeling: int = Field(
        description="Sentimiento del mensaje, 2: positivo, 1: negativo, 0: neutral"
    )
    Need: str = Field(
        description="Ayuda solicitada"
    )
    Suport_type: int = Field(
        description="Tipo de soporte: 1: necesita contacto humano, 0: necesita soporte técnico")

class LLMModel:
    """
    Base class for all LLM models.
    This class should be inherited by any specific LLM model implementation.
    """

    def __init__(self, model_name: str):
        self.model_name = model_name

    def classify(self, text: str) -> str:
        response = chat(
            messages=[
                {
                'role': 'user',
                'content': promt_template + text,
                }
            ],
            model='gemma3:12b',
            format=Classification.model_json_schema(),
            )
        
        llm_response = Classification.model_validate(response.message.content)

        return {
            "Classification": llm_response.Classification,
            "Feeling": llm_response.Feeling,
            "Need": llm_response.Need,
            "Suport_type": llm_response.Suport_type
        }