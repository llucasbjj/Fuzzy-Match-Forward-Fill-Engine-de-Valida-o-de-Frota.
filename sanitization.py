import re

class PlateSanitizer:
    """
    Camada 1: Sanitização e Heurística.
    Responsável por limpar a entrada de dados e corrigir erros humanos comuns de digitação.
    """

    # Mapa de confusão visual comum (Heurística)
    # Caracteres que humanos confundem frequentemente ao digitar placas
    HEURISTIC_MAP = {
        '0': 'O',  # Zero digitado como letra O
        'O': '0',  # Letra O digitada como Zero (reverso, depende do padrão)
        'G': '6',
        '6': 'G',
        'Z': '2',
        '2': 'Z',
        '1': 'I',
        'I': '1',
        'B': '8',
        '8': 'B',
        'Q': '0',
        # Adicione mais conforme a necessidade operacional
    }

    @staticmethod
    def strict_clean(value):
        """
        Limpeza estrita: Remove tudo que não é alfanumérico e converte para maiúsculo.
        Ex: 'abc-1234 ' -> 'ABC1234'
        """
        if not value:
            return ""
        # Converte para string, maiúsculo, remove espaços nas pontas
        v = str(value).upper().strip()
        # Remove qualquer coisa que NÃO seja letra (A-Z) ou número (0-9)
        return re.sub(r'[^A-Z0-9]', '', v)

    @staticmethod
    def generate_variations(clean_plate):
        """
        Gera TODAS as variações possíveis da placa baseadas no mapa heurístico (Combinatorial).
        Ex: 'ZZ' -> 'ZZ', 'Z2', '2Z', '22'.
        """
        import itertools
        
        # Para cada caractere, lista as opções possíveis.
        # Se estiver no mapa, opções são: [original, heurística]
        # Se não, opção é: [original]
        char_options = []
        for char in clean_plate:
            options = {char} # Set para deduplicar
            if char in PlateSanitizer.HEURISTIC_MAP:
                options.add(PlateSanitizer.HEURISTIC_MAP[char])
            char_options.append(list(options))
            
        # Gera produto cartesiano de todas as opções
        # Ex: [R] x [R] x [M] x [5] x [D] x [Z,2] x [Z,2]
        combinations = itertools.product(*char_options)
        
        # Junta os caracteres para formar strings
        variations = {''.join(combo) for combo in combinations}
        
        return variations

if __name__ == "__main__":
    # Teste rápido manual
    s = PlateSanitizer
    print(f"Teste ' abc-1234 ': {s.strict_clean(' abc-1234 ')}")
    print(f"Variações 'OBC1234': {s.generate_variations('OBC1234')}")
