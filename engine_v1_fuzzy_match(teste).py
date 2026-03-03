"""
#Algorithm: Heuristic Supply Chain Validator (v1.0)
#Description: 
    #- Implements 'Forward Fill' for context inheritance in hierarchical logistics sheets.
    #- Uses 'Fuzzy Matching' logic with weighted scoring (70/30) for identity verification.
    3- Applied 'Character-Mapping Heuristics' to mitigate human input errors in license plates.
#Author: Lucas de Moraes Bento da Silva
#Course: Software Engineering - UFR
"""



# ==========================================
# FUNÇÕES GLOBAIS
# ==========================================
def higienizar(valor):
    if not valor: return ""
    # Forçamos string para evitar erro caso o n8n envie como número
    v = str(valor).upper().strip()
    limpo = "".join(c for c in v if (c >= 'A' and c <= 'Z') or (c >= '0' and c <= '9'))
    # Regras de substituição para falha humana (G->6, 4->A, 0->O)
    return limpo.replace('G', '6').replace('4', 'A').replace('0', 'O')

# ==========================================
# PROCESSAMENTO DOS 4 BLOCOS INTEGRADOS
# ==========================================
melhor_match = None
maior_score = 0.0

# Variáveis de Memória para o Bloco 2 (Forward Fill)
motorista_memoria = "SEM MOTORISTA"
frota_memoria = "N/A"

# Percorremos a lista consolidada (Planilha + Nota injetada)
for item in _items:
    # Acesso defensivo ao JSON (Evita erro de Dict/Null)
    try:
        dados = item["json"] if isinstance(item, dict) and "json" in item else item
    except:
        continue
        
    if not dados: continue

    # --- BLOCO 1: Extração da Nota (Injetada pelo Edit Fields) ---
    p_nota = higienizar(dados.get("placa_nota", ""))
    m_nota = str(dados.get("motorista_nota", "") or "").upper().strip()

    # --- BLOCO 2: Processamento e Forward Fill (Planilha) ---
    p_plan_raw = dados.get("placa") or dados.get("Placa")
    m_plan_raw = dados.get("Motorista") or dados.get("motorista")
    f_plan_raw = dados.get("Frota") or dados.get("frota")

    # Atualiza a memória se encontrar novos dados de motorista/frota
    if m_plan_raw and str(m_plan_raw).strip():
        motorista_memoria = str(m_plan_raw).replace('?', '').upper().strip()
    if f_plan_raw and str(f_plan_raw).strip():
        frota_memoria = str(f_plan_raw)

    # --- BLOCO 3: Engine de Match (70/30) ---
    # Só tentamos o match se houver uma placa nesta linha da planilha
    if p_plan_raw:
        p_plan_limpa = higienizar(p_plan_raw)
        
        # Match de Placa (70%)
        score_p = 1.0 if p_plan_limpa == p_nota and p_nota != "" else 0.0
        
        # Match de Motorista (30%) - Usa a memória atual do Forward Fill
        score_m = 0.0
        if m_nota and motorista_memoria:
            if m_nota in motorista_memoria or motorista_memoria in m_nota:
                score_m = 1.0
        
        # Cálculo final (Se nota não tem motorista, score foca 100% na placa)
        score_atual = (score_p * 0.7) + (score_m * 0.3) if m_nota else score_p

        # Se for o melhor até agora, guarda
        if score_atual > maior_score:
            maior_score = score_atual
            melhor_match = {
                "placa_oficial": str(p_plan_raw).upper(),
                "placa_limpa": p_plan_limpa,
                "motorista": motorista_memoria,
                "frota": frota_memoria
            }
        
        # Otimização: Se achou 100%, para a execução do loop
        if maior_score == 1.0: break

# --- BLOCO 4: Retorno e Debug Final ---
status_final = "SUCESSO" if maior_score >= 0.7 else "DIVERGÊNCIA"

return [{
    "validacao": {
        "status": status_final,
        "confianca": f"{maior_score * 100:.2f}%",
        "mensagem": "Validado com sucesso" if status_final == "SUCESSO" else "Divergência de dados"
    },
    "resultado": melhor_match if melhor_match else "Nenhum Match Encontrado",
    "debug": {
        "total_registros_base": len(_items),
        "entrada_procurada": {"placa": p_nota, "motorista": m_nota}
    }
}]
