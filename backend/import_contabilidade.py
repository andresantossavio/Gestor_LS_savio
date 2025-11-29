import csv
import datetime
from typing import List, Dict, Tuple, Optional


def _parse_valor_brl_to_centavos(s: str) -> Optional[int]:
    if not s:
        return None
    s = s.strip().replace("R$", "").replace(" ", "")
    s = s.replace(".", "").replace(",", ".")
    try:
        v = float(s)
        return int(round(v * 100))
    except Exception:
        return None


def _parse_percent_to_mil(s: str) -> Optional[int]:
    if not s:
        return None
    s = s.strip().replace("%", "")
    s = s.replace(",", ".")
    try:
        v = float(s)
        return int(round(v * 10))  # 50% => 500 milésimos
    except Exception:
        return None


def detectar_colunas(csv_header: List[str]) -> Tuple[int, int, int, List[int]]:
    cliente_idx = next((i for i, h in enumerate(csv_header) if h.strip().lower().startswith("cliente")), -1)
    data_idx = next((i for i, h in enumerate(csv_header) if h.strip().lower().startswith("data")), -1)
    valor_idx = next((i for i, h in enumerate(csv_header) if "valor" in h.lower()), -1)
    socio_idxs = [i for i in range(valor_idx + 1, len(csv_header))]
    socio_idxs = [i for i in socio_idxs if csv_header[i].strip() != ""]
    return cliente_idx, data_idx, valor_idx, socio_idxs


def carregar_csv_contabilidade(filepath: str) -> List[Dict]:
    rows: List[List[str]] = []
    for encoding in ["latin-1", "utf-8-sig"]:
        try:
            with open(filepath, "r", encoding=encoding, newline="") as f:
                reader = csv.reader(f, delimiter=";")
                rows = list(reader)
            break
        except Exception:
            continue

    if not rows:
        return []

    header = rows[0]
    cliente_idx, data_idx, valor_idx, socio_idxs = detectar_colunas(header)

    entries: List[Dict] = []
    for row in rows[1:]:
        if all((c is None or str(c).strip() == "") for c in row):
            continue
        cliente_nome = row[cliente_idx].strip() if 0 <= cliente_idx < len(row) else None
        data_str = row[data_idx].strip() if 0 <= data_idx < len(row) else None
        valor_str = row[valor_idx].strip() if 0 <= valor_idx < len(row) else None

        data_dt = None
        if data_str:
            for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
                try:
                    data_dt = datetime.datetime.strptime(data_str, fmt).date()
                    break
                except Exception:
                    continue

        valor_centavos = _parse_valor_brl_to_centavos(valor_str)

        participacoes: List[Dict] = []
        for i in socio_idxs:
            nome_coluna = header[i].strip()
            if not nome_coluna:
                continue
            pct_str = row[i].strip() if i < len(row) else ""
            pct_mil = _parse_percent_to_mil(pct_str)
            if pct_mil is None:
                continue
            participacoes.append({"socio_nome": nome_coluna, "percentual_mil": pct_mil})

        entries.append({
            "cliente_nome": cliente_nome,
            "data": data_dt,
            "valor_centavos": valor_centavos,
            "participacoes": participacoes
        })
    return entries
