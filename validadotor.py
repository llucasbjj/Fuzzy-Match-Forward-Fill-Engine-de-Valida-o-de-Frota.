import gspread
from google.oauth2.service_account import Credentials
import os
import time
from sanitization import PlateSanitizer
from rapidfuzz import process, fuzz, distance

# Constantes
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
CREDENTIALS_FILE = "credentials-*****-********.json"

class PlateValidator:
    """
    Camada 2: Validação Lógica e Regras de Negócio (v3.0 Fuzzy).
    Gerencia conexão com Google Sheets e aplica regras de autorização com score de similaridade.
    """

    def __init__(self, credentials_path=CREDENTIALS_FILE):
        self.credentials_path = credentials_path
        self._authorized_plates = {}
        self.client = None
        self.last_load_time = 0
        self.cache_duration = 300 
        
        # Conecta ao iniciar
        self.connect_and_load()

    def connect_and_load(self):
        """Conecta e carrega dados."""
        try:
            self._connect()
            self._load_plates()
            return True, "Conectado com sucesso."
        except Exception as e:
            return False, f"Erro de conexão: {str(e)}"

    def _connect(self):
        if not os.path.exists(self.credentials_path):
            raise FileNotFoundError(f"Arquivo de credenciais '{self.credentials_path}' não encontrado.")
            
        creds = Credentials.from_service_account_file(self.credentials_path, scopes=SCOPES)
        self.client = gspread.authorize(creds)

    def _load_plates(self):
        """Carrega e sanitiza a lista de placas autorizadas (Layout Fixo: Col C, Linha 8+)."""
        if not self.client:
            return

        print("Iniciando carga de dados do Google Sheets...")
        
        # Tenta abrir a planilha
        spreadsheets = self.client.list_spreadsheet_files()
        if not spreadsheets:
            raise Exception("Nenhuma planilha encontrada compartilhada com a conta de serviço.")

        sheet = self.client.open_by_key(spreadsheets[0]['id'])
        print(f"Acessando planilha: {sheet.title}")
        
        worksheet = None
        possible_tabs = ["Relação NFe", "Relação placa/motorista", "Placas", "Página1"]
        
        for tab_name in possible_tabs:
            try:
                worksheet = sheet.worksheet(tab_name)
                print(f"Aba '{tab_name}' encontrada.")
                break
            except:
                continue
        
        if not worksheet:
            worksheet = sheet.get_worksheet(0)
            print(f"Aviso: Nenhuma das abas padrão encontrada. Usando a primeira aba: '{worksheet.title}'")

        # --- ESTRUTURA FIXA (Solicitada pelo Usuário) ---
        # Coluna B (Índice 2): Motorista
        # Coluna C (Índice 3): Placa
        # Dados começam na Linha 8
        print("Lendo Base a partir da linha 8...")
        
        try:
            # Pega todas as linhas para evitar desalinhamento entre as colunas B e C
            all_rows = worksheet.get_all_values()
            
            # gspread retorna a lista começando da linha 1.
            # Se a lista tiver menos de 8 itens, não tem dados válidos.
            if len(all_rows) < 8:
                rows_data = []
            else:
                rows_data = all_rows[7:]
                
        except Exception as e:
            print(f"Erro ao ler linhas da planilha: {e}")
            rows_data = []

        # Limpa o map atual (agora é um dicionário {placa: motorista})
        self._authorized_plates.clear()
        self.debug_last_loaded = [] 
        
        # Sanitização
        count = 0
        for row in rows_data:
            raw_driver = row[1].strip() if len(row) > 1 else ""
            raw_plate = row[2].strip() if len(row) > 2 else ""
            
            # Sanitiza
            clean = PlateSanitizer.strict_clean(raw_plate)
            
            # Regra: Se tiver texto na Coluna C (Placa Válida), é adicionado ao Dict.
            if clean: 
                self._authorized_plates[clean] = raw_driver
                if len(self.debug_last_loaded) < 10: 
                    self.debug_last_loaded.append(f"{raw_plate} -> {clean} (Mot: {raw_driver})")
                count += 1
                
        self.last_load_time = time.time()
        print(f"Base carregada: {count} placas ativas.")
        print(f"Amostra: {self.debug_last_loaded}")



    def validate_plate_fuzzy(self, user_input):
        """
        Valida a placa usando lógica Fuzzy (v3.1).
        Retorna o score de confiança, a melhor correspondência e SUCESSIVAS opções (Top 3).
        """
        clean_input = PlateSanitizer.strict_clean(user_input)
        
        # Estrutura de retorno padrão
        response = {
            'is_match': False,
            'confidence': 0.0,
            'best_match': None,
            'driver': '',
            'input_clean': clean_input,
            'message': "Iniciado",
            'edit_distance': -1,
            'candidates': [] # Lista de {plate, score, distance}
        }
        
        if not clean_input:
            response['message'] = "Entrada vazia."
            return response
            
        if not self._authorized_plates:
            response['message'] = "Base de dados vazia."
            return response

        # 1. Tentativa de Match Exato (100%) - O(1)
        if clean_input in self._authorized_plates:
            response.update({
                'is_match': True,
                'confidence': 100.0,
                'best_match': clean_input,
                'driver': self._authorized_plates[clean_input],
                'message': "Match Exato (100%)",
                'edit_distance': 0,
                'candidates': [{'plate': clean_input, 'score': 100.0, 'dist': 0}]
            })
            return response
            
        # 1.5. Busca Heurística (Combinatorial) - O(1) Cache-like
        # Gera todas as variações possíveis (Ex: 0 <-> O, Z <-> 2)
        # Se alguma existir na base, é a nossa melhor aposta.
        variations = PlateSanitizer.generate_variations(clean_input)
        
        # Filtra apenas as que existem na base
        valid_variations = [v for v in variations if v in self._authorized_plates]
        
        if valid_variations:
            # Encontrou pelo menos uma!
            # Pega a primeira (se tiver mais de uma, qualquer uma serve pois são visualmente idênticas)
            best_match = valid_variations[0]
            dist = int(distance.Levenshtein.distance(clean_input, best_match)) # Recalcula distância real
            
            response.update({
                'is_match': True,
                'confidence': 99.0, # Quase 100%, mas marca como inferência
                'best_match': best_match,
                'driver': self._authorized_plates.get(best_match, ''),
                'message': "Correção Heurística (Visual)",
                'edit_distance': dist,
                'candidates': [{'plate': best_match, 'score': 99.0, 'dist': dist, 'note': 'Heurística'}]
            })
            return response

        # 2. Match Fuzzy (RapidFuzz) - Top 3
        choices = list(self._authorized_plates)
        
        # extract retorna lista de tuplas (match, score, index)
        # limit=3 para pegar os 3 melhores
        results = process.extract(clean_input, choices, scorer=fuzz.ratio, limit=3)
        
        if not results:
             response['message'] = "Nenhuma correspondência."
             return response
            
        # Processa os candidatos
        candidates = []
        for match, score, _ in results:
            dist = int(distance.Levenshtein.distance(clean_input, match))
            candidates.append({
                'plate': match,
                'score': round(score, 1),
                'dist': dist
            })
            
        # O melhor é o primeiro
        best_candidate = candidates[0]
        best_match = best_candidate['plate']
        score = best_candidate['score']
        dist = best_candidate['dist']
        
        # Definição de Limiares (Mantendo a lógica v3.0)
        # >= 85: Alta confiança 
        # >= 70 E Dist <= 2: Aceitável 
        
        is_high_confidence = score >= 85.0 or (score >= 70.0 and dist <= 2)
        
        response.update({
            'is_match': is_high_confidence,
            'confidence': score,
            'best_match': best_match,
            'driver': self._authorized_plates.get(best_match, '') if is_high_confidence else '',
            'message': f"Match Aproximado: {best_match}" if is_high_confidence else "Baixa similaridade",
            'edit_distance': dist,
            'candidates': candidates
        })
        
        return response

    def force_reload(self):
        """Força recarga dos dados da planilha."""
        self._load_plates()
