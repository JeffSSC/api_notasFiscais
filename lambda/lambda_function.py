import json
import base64

# Funções utilitárias para leitura de documentos, filtragem de texto
from utils.textract_utils import read_document
from utils.nltk_utils import filter_text
from models.responseModel import responseModel, responseJSON
from utils.bedrock_utils import analyze_image
from utils.s3_utils import upload_to_s3


def lambda_handler(event, context):
    content = event['content']

    # Decodifica o conteúdo para bytes
    decode_content = base64.b64decode(content)

    # Lê o documento usando Textract e retorna texto bruto
    document = read_document(content)

    # Constrói um modelo de resposta a partir do texto extraído
    responseTextract = responseModel(document)

    # Filtra o texto para remover ruídos ou informações irrelevantes
    filtered_text = filter_text(responseTextract)

    # Analisa o texto filtrado com um serviço de IA
    AIresponse_raw = analyze_image(filtered_text)

    # Converte a resposta bruta da IA para formato JSON
    response = responseJSON(AIresponse_raw)

    # Obtém a forma de pagamento identificada ou usa 'outros' como padrão
    forma_pagamento = response.get('forma_pgto', 'outros')

    # Faz upload da imagem/dados originais para S3 com metadados de forma de pagamento
    upload_to_s3(
        bucket_name="sprint-notas-fiscais",
        file_bytes=decode_content,
        file_extension="jpg",
        forma_pagamento=forma_pagamento
    )

    # Faz upload da resposta JSON para S3 no mesmo bucket
    upload_to_s3(
        bucket_name="sprint-notas-fiscais",
        file_bytes=json.dumps(response, indent=2).encode("utf-8"),
        file_extension="json",
        forma_pagamento=forma_pagamento
    )

    return response