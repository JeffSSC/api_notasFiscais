import boto3
import base64

def read_document(content):
    # Inicializa o cliente Textract da AWS
    textract = boto3.client('textract')
    decode_content = base64.b64decode(content)
    response = textract.detect_document_text(Document={'Bytes': decode_content})

    return response