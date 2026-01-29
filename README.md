Resumo: Algoritmo em Python integrado ao n8n para validação de registros logísticos. Implementa Forward Fill para herança de dados hierárquicos e Scoring Ponderado (70/30) para normalização de erros de input humano em placas e nomes de motoristas






📂 G10 Supply Chain Auth - Validador de Abastecimento Inteligente
Este projeto consiste em uma engine de validação desenvolvida em Python integrada ao n8n, projetada para sanitizar e cruzar registros de abastecimento de frota pesada (G10 Transportes), mitigando erros humanos de entrada e garantindo a integridade dos dados operacionais.

🎯 Problemas Resolvidos
Erros de Input Humano: Substituição comum de caracteres em placas (ex: 'G' por '6', '0' por 'O').

Dados Hierárquicos (Planilha Visual): O sistema resolve a ausência de dados em carretas vinculadas através de um algoritmo de Forward Fill.

Identidade Flexível: Validação de motoristas através de Score Ponderado, permitindo correspondências parciais ou nomes abreviados.

🛠️ Arquitetura Técnica
1. Higienização e Normalização Agressiva
Diferente de uma comparação simples, o sistema aplica uma limpeza que remove caracteres especiais e realiza substituições baseadas em falhas comuns de digitação de placas no setor logístico:

G → 6

4 → A

0 → O

2. Algoritmo de Forward Fill (Herança de Contexto)
Em planilhas logísticas, é comum que o Motorista e a Frota apareçam apenas na linha da Tração, deixando as linhas das carretas vazias. O código mantém um estado de memória (motorista_memoria) que propaga o último condutor válido para as linhas subsequentes.

3. Engine de Scoring Ponderado (70/30)
O veredito de sucesso é baseado em um cálculo de probabilidade:

Placa (Peso 0.7): Identificação física do veículo (Match exato pós-higienização).

Motorista (Peso 0.3): Identificação subjetiva (Match parcial/inclusão de string).

Threshold: O sistema exige um score mínimo de 0.7 para aprovação automática.

🚀 Como Executar
No n8n:

Conecte um nó de Google Sheets (Base Histórica).

Conecte um nó de Edit Fields (Dados da Nota).

Utilize o nó Code (Python) no modo Run Once for All Items.

Variáveis Necessárias:

placa_nota (String)

motorista_nota (String)

🧑‍💻 Tecnologias
Python 3.x (Lógica de processamento)

n8n (Orquestração de workflow)

Google Sheets API (Data Source)
