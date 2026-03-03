FuzzyMachine: Motor Inteligente de Validação e Correção de Placas
Um módulo leve e de alta performance desenvolvido em Python para validação, sanitização e auto-correção de placas veiculares (padrão Mercosul e Antigo). Desenvolvido para atuar como uma camada de Programação Defensiva em pipelines de dados e robôs de RPA logísticos.

🎯 O Problema (Por que este módulo existe?)
Em operações logísticas de grande escala, a entrada de dados de placas de veículos sofre com dois grandes gargalos:

Erros Humanos (Typos): Digitação incorreta em planilhas (ex: confundir a letra O com o número 0, ou a letra I com o número 1). Exemplo real: Digitar SPT1O14 em vez de SPT1014.

Falhas de OCR: Leitores de PDF e softwares de visão computacional frequentemente leem caracteres arranhados em notas fiscais de forma equivocada (ex: RRMSD32 em vez de RRM5D32).

Quando esses dados "sujos" chegam ao ERP ou banco de dados, eles geram falhas de integração, rejeição de notas fiscais e quebra de relatórios de frota.

💡 A Solução: Fuzzy Logic & Regex
O FuzzyMachine não faz apenas uma verificação booleana (Verdadeiro/Falso). Ele atua como um corretor ortográfico focado em logística:

Sanitização Extrema (Regex): Remove caracteres especiais, espaços, traços e sujeiras invisíveis, padronizando tudo para Uppercase alfanumérico.

Validação de Formato: Identifica se a string resultante atende à matriz do padrão Brasileiro Antigo (ABC1234) ou Mercosul (ABC1D23).

Auto-Correção com RapidFuzz: Utiliza algoritmos de Levenshtein Distance (Lógica Fuzzy) para comparar a placa suja contra um banco/dicionário de frota conhecida. Se a placa digitada tiver um nível de confiança alto (ex: 85%+) de semelhança com uma placa real da frota, o motor corrige o erro automaticamente e devolve a placa perfeita para o sistema.

🚀 Impacto no Negócio
Mitigação de Erros: Redução drástica de chamados de suporte e reprocessamento de notas fiscais por "Placa Não Encontrada".

Resiliência para RPAs: Permite que robôs de automação continuem operando mesmo quando ingerem planilhas com baixa qualidade de digitação, sem interromper o fluxo com paradas desnecessárias.

💻 Exemplo de Uso
Como este módulo se comporta na prática ao ser importado por outros sistemas:

Python
from src.validator import PlateValidator

# Inicializa o validador com uma frota conhecida (Pode vir de um Banco de Dados)
frota_valida = ["SPT1014", "RRM5D32", "ABC1234"]
validador = PlateValidator(frota_conhecida=frota_valida)

# Cenário 1: Erro humano clássico (Letra O no lugar do zero)
placa_suja = "SPT1O14" 
resultado = validador.validate_plate_fuzzy(placa_suja)
print(resultado)
# Output: {'is_match': True, 'best_match': 'SPT1014', 'confidence': 88.5, 'status': 'Auto-Corrigido'}

# Cenário 2: Erro de leitura OCR (S no lugar do 5)
placa_ocr = "Placa: RRMSD32- MT"
resultado = validador.validate_plate_fuzzy(placa_ocr)
print(resultado)
# Output: {'is_match': True, 'best_match': 'RRM5D32', 'confidence': 90.0, 'status': 'Auto-Corrigido'}
🛠️ Tecnologias Utilizadas
Python 3.10+

RapidFuzz: Biblioteca C++ otimizada para Python, garantindo comparação de strings em microssegundos (muito mais rápida que o tradicional FuzzyWuzzy).

Expressões Regulares (re): Para pattern matching rigoroso.

"Dados limpos não são um luxo, são a fundação de qualquer automação estável."
