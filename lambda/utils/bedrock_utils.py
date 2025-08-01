import boto3
import base64
import json

def analyze_image(text):
    client = boto3.client('bedrock-runtime')
    # Identificador do modelo a ser utilizado
    modelID = 'amazon.nova-pro-v1:0'
    # Constroi a mensagem de usuário com instruções de extração e o texto da nota
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "text": f"""
Você é um sistema que extrai dados estruturados de notas fiscais brasileiras.
 
A partir do texto a seguir, extraia os seguintes campos e retorne um JSON:
- nome_emissor
- cnpj_emissor
- endereco_emissor
- cnpj_cpf_consumidor
- data_emissao
- numero_nota_fiscal
- serie_nota_fiscal
- valor_total
- forma_pgto
 
Texto da nota: {text}
 
    Sua resposta DEVE conter apenas um JSON bruto e NADA MAIS.
    Sem explicações, títulos, texto adicional ou blocos de código.
    Apenas o conteúdo JSON, direto, puro e sem formatação adicional.
 
⚠️ Regras importantes:
 
1. O campo **forma_pgto** deve ser preenchido com uma das opções exatas e minúsculas:
    - "dinheiro"
    - "cartao_credito"
    - "cartao_debito"
    - "pix"
    - "outros"
   
    Identifique com base em palavras-chave:
    - "dinheiro", "valor em espécie" → **dinheiro**
    - "cartão crédito", "credito", "Cartão Crédito" → **cartao_credito**
    - "cartão débito", "debito", "Cartão Débito" → **cartao_debito**
    - "pix" → **pix**
    - Nenhuma ou outra forma → **outros**
 
2. Validações obrigatórias por campo:
 
    - **nome_emissor**:
        - Deve conter pelo menos duas palavras legíveis e corretamente escritas em português.
        - Se tiver erros ortográficos, palavras incompletas ou truncadas (ex: "COMERY DE ALIMENIUS"), retorne **None**.
   
    - **cnpj_emissor**:
       - O campo **cnpj_emissor** deve conter exatamente 14 dígitos numéricos válidos.
  - Formatos aceitos:
    - "00000000000000"
    - "00.000.000/0000-00"
  - Se tiver menos ou mais de 14 dígitos, ou se os separadores estiverem errados, ou se for fictício/inválido → **retorne None**.
  - Exemplo inválido: "251.513/2082-92" → **None**
   
   - **endereco_emissor**:
    - O campo **endereco_emissor** deve conter um endereço **completo e legível**, com os seguintes elementos obrigatórios:
        - **Logradouro** (ex: "Rua", "Avenida", "Alameda") — escrito corretamente.
        - **Número** do imóvel (ex: "123", "1020").
        - **Cidade** ou **Estado** (ex: "São Paulo", "RJ").
 
    - **Rejeite e retorne None se o endereço contiver**:
        - Texto truncado ou ilegível.
        - Palavras ou abreviações incomuns ou corrompidas.
        - Apenas partes soltas como CEP, bairro, cidade ou número isolado.
        - Qualquer elemento irreconhecível misturado com números sem formatação clara.
 
    - **Exemplos inválidos que devem retornar None**:
        - "AVENIDA PRESIDENTE JUSCELINO KUBITSCHEK DE (II (VETRA) 50 00 LOJA 1052 IGUATEMI SAG JUSH on RIO PRETO"
        - "Rua das Flores" (sem número e cidade/estado)
        - "123" (número isolado)
        - "São Paulo" (cidade sozinha)
        - "CEP: 88047-902" (CEP isolado)
        - **"VIA: TR VP 0003. 6200 - PAVMTO PRIMEIRO SUO 1, BAIRRO: CARLANDS, CEP: 88047-902, FLORIANOPOLIS-SC"**
 
    - **Exemplos válidos**:
        - "Rua das Flores, 123, São Paulo - SP"
        - "Avenida Paulista, 1000, São Paulo - SP"
        - "Alameda Santos, 250, São Paulo"
   
    - **cnpj_cpf_consumidor**:
        - Aceita CNPJ ou CPF válidos:
            - CPF: 000.000.000-00 ou 00000000000
            - CNPJ: mesmo formato do emissor
        - Formatos inválidos, incompletos ou corrompidos → **None**
   
    - **data_emissao**:
        - Deve estar em formato DD/MM/AAAA.
        - Se a data estiver incompleta, com mês inválido ou fora desse padrão → **None**
   
    - **numero_nota_fiscal**:
        - Deve ser um número inteiro.
        - Se contiver letras ou estiver truncado → **None**
   
    - **serie_nota_fiscal**:
        - Deve ser um número ou código alfanumérico curto, geralmente após “SÉRIE” ou “SAT N”.
        - Se ausente ou ilegível → **None**
        - Se tiver menos de 9 numeros → **None**
   
    - **valor_total**:
        - Deve ser um número decimal positivo com duas casas decimais.
        - Ex: 55.37
        - Se for zero, ausente ou inválido → **None**
   
    - **forma_pgto**:
        - Veja a regra nº 1. Deve obedecer estritamente às palavras permitidas.
 
3. Regra geral:
    - Sempre prefira retornar **None** se o valor estiver:
        - Ausente
        - Com erro de digitação
        - Incompleto
        - Ilegível ou truncado
        - Mal formatado
    - Se possível busque no seu banco de dados informações que você possa consertar
 
"""
                }
            ]
        }
    ] 
    system = [ { "text": "Você é um analista de notas fiscais." } ]

    # Executa a chamada ao modelo no Bedrock
    responseIA = client.converse(
    
        modelId=modelID,
        messages=messages,
        system=system
        )
    
    # Extrai o JSON bruto retornado pelo modelo
    text = responseIA["output"]["message"]["content"][0]["text"]
    # Limpa marcadores de bloco de código do JSON retornado
    text_clean = clean_text(text)

    return text_clean

def clean_text(texto):
    if texto.startswith("```json\n"):
        texto = texto[len("```json\n"):]
    if texto.endswith("\n```"):
        texto = texto[:-len("\n```")]
    return texto