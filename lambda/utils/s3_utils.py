import boto3
import json
from datetime import datetime, timedelta, timezone

def upload_to_s3(bucket_name, file_bytes, file_extension, forma_pagamento):
    s3 = boto3.client('s3')

    # Define o fuso horário UTC-3 (horário de Brasília)
    utc_minus_3 = timezone(timedelta(hours=-3))

    timestamp = datetime.now(utc_minus_3).strftime("%Y-%m-%dT%H-%M-%S")

    # Seleciona pasta com base no método de pagamento
    folder = "dinheiro" if forma_pagamento.lower() in ["dinheiro", "pix"] else "outros"

    # Monta nome do arquivo com timestamp e extensão
    filename = f"notas-{timestamp}.{file_extension}"
    s3_path = f"{folder}/{filename}"

    # Define o Content-Type baseado na extensão do arquivo
    content_type = "application/json" if file_extension == "json" else f"image/{file_extension}"

    # Realiza o upload do objeto ao bucket S3
    s3.put_object(
        Bucket=bucket_name,
        Key=s3_path,
        Body=file_bytes,
        ContentType=content_type
    )

    return s3_path
