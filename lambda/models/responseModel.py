import json  

def responseModel(content):
    # Obtém a lista de blocos extraídos (Textract 'Blocks')
    summary = content['Blocks']
    # Lista para armazenar trechos de texto encontrados
    text = []

    # Para cada bloco, adiciona o texto (campo 'Text') à lista, se existir
    for i in summary:
        if 'Text' in i:
            text.append(i['Text'])

    # Retorna lista de strings correspondentes aos textos extraídos
    return text

def responseJSON(AIresponse):
    """
    Converte uma string JSON da IA em dicionário Python,
    extrai campos específicos e normaliza valores nulos.
    """
    try:
        # Converte a string JSON para dicionário
        text = json.loads(AIresponse)
    except json.JSONDecodeError as e:
        raise ValueError(f"Erro ao decodificar JSON: {e}")

    # Extrai os campos com segurança usando .get()
    rawResponse = {
        'nome_emissor': text.get('nome_emissor'),
        'CNPJ_emissor': text.get('cnpj_emissor'),
        'endereco_emissor': text.get('endereco_emissor'),
        'CNPJ_CPF_consumidor': text.get('cnpj_cpf_consumidor'),
        'data_emissao': text.get('data_emissao'),
        'numero_nota_fiscal': text.get('numero_nota_fiscal'),
        'serie_nota_fiscal': text.get('serie_nota_fiscal'),
        'valor_total': text.get('valor_total'),
        'forma_pgto': text.get('forma_pgto')
    }

    return replace_null_values(rawResponse)

def replace_null_values(data):
    """
    Substitui valores None ou strings que representam 'nulo' por None 
    em estruturas aninhadas de dicionários ou listas.
    """
    null_equivalents = {'null', 'None', 'NULL', 'nulo', 'N/A', ''}

    if isinstance(data, dict):
        return {key: replace_null_values(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [replace_null_values(item) for item in data]
    elif data is None:
        return "None"
    elif isinstance(data, str) and data.strip() in null_equivalents:
        return "None"
    else:
        return data
