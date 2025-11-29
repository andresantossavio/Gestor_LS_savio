"""
CRUD operations para Feriados.
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from database.models import Feriado, Municipio
from datetime import date
from typing import List, Optional, Dict


def criar_feriado(
    db: Session,
    data: date,
    nome: str,
    tipo: str,
    uf: Optional[str] = None,
    municipio_id: Optional[int] = None,
    recorrente: bool = False,
    criado_por: Optional[int] = None
) -> Feriado:
    """
    Cria um novo feriado.
    
    Args:
        db: Sessão do banco de dados
        data: Data do feriado
        nome: Nome do feriado
        tipo: 'nacional', 'estadual' ou 'municipal'
        uf: UF (obrigatório se tipo='estadual')
        municipio_id: ID do município (obrigatório se tipo='municipal')
        recorrente: Se repete anualmente
        criado_por: ID do usuário que criou
    
    Returns:
        Feriado criado
    
    Raises:
        ValueError: Se validações falharem
    """
    # Validações
    if tipo not in ['nacional', 'estadual', 'municipal']:
        raise ValueError("Tipo deve ser 'nacional', 'estadual' ou 'municipal'")
    
    if tipo == 'estadual' and not uf:
        raise ValueError("UF é obrigatória para feriados estaduais")
    
    if tipo == 'municipal' and not municipio_id:
        raise ValueError("Município é obrigatório para feriados municipais")
    
    # Se for municipal, obter a UF do município
    if tipo == 'municipal' and municipio_id:
        municipio = db.query(Municipio).filter(Municipio.id == municipio_id).first()
        if not municipio:
            raise ValueError("Município não encontrado")
        uf = municipio.uf
    
    feriado = Feriado(
        data=data,
        nome=nome,
        tipo=tipo,
        uf=uf.upper() if uf else None,
        municipio_id=municipio_id,
        recorrente=recorrente,
        criado_por=criado_por
    )
    
    db.add(feriado)
    db.commit()
    db.refresh(feriado)
    return feriado


def listar_feriados(
    db: Session,
    tipo: Optional[str] = None,
    uf: Optional[str] = None,
    municipio_id: Optional[int] = None,
    ano: Optional[int] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None
) -> List[Feriado]:
    """
    Lista feriados com filtros opcionais.
    
    Args:
        db: Sessão do banco de dados
        tipo: Filtro por tipo
        uf: Filtro por UF
        municipio_id: Filtro por município
        ano: Filtro por ano
        data_inicio: Data inicial do período
        data_fim: Data final do período
    
    Returns:
        Lista de feriados filtrada e ordenada por data
    """
    query = db.query(Feriado)
    
    # Aplicar filtros
    if tipo:
        query = query.filter(Feriado.tipo == tipo)
    
    if uf:
        query = query.filter(Feriado.uf == uf.upper())
    
    if municipio_id:
        query = query.filter(Feriado.municipio_id == municipio_id)
    
    if ano:
        query = query.filter(
            and_(
                Feriado.data >= date(ano, 1, 1),
                Feriado.data <= date(ano, 12, 31)
            )
        )
    
    if data_inicio:
        query = query.filter(Feriado.data >= data_inicio)
    
    if data_fim:
        query = query.filter(Feriado.data <= data_fim)
    
    return query.order_by(Feriado.data).all()


def listar_feriados_por_periodo(
    data_inicio: date,
    data_fim: date,
    municipio_id: Optional[int],
    db: Session
) -> List[Feriado]:
    """
    Lista feriados aplicáveis a um município em um período.
    Inclui feriados nacionais, estaduais (da UF) e municipais.
    
    Args:
        data_inicio: Data inicial
        data_fim: Data final
        municipio_id: ID do município (None para apenas nacionais)
        db: Sessão do banco de dados
    
    Returns:
        Lista de feriados no período
    """
    query = db.query(Feriado).filter(
        Feriado.data >= data_inicio,
        Feriado.data <= data_fim
    )
    
    if municipio_id:
        municipio = db.query(Municipio).filter(Municipio.id == municipio_id).first()
        if municipio:
            query = query.filter(
                or_(
                    Feriado.tipo == "nacional",
                    and_(Feriado.tipo == "estadual", Feriado.uf == municipio.uf),
                    and_(Feriado.tipo == "municipal", Feriado.municipio_id == municipio_id)
                )
            )
    else:
        query = query.filter(Feriado.tipo == "nacional")
    
    return query.order_by(Feriado.data).all()


def buscar_feriado_por_id(feriado_id: int, db: Session) -> Optional[Feriado]:
    """
    Busca feriado por ID.
    
    Args:
        feriado_id: ID do feriado
        db: Sessão do banco de dados
    
    Returns:
        Feriado encontrado ou None
    """
    return db.query(Feriado).filter(Feriado.id == feriado_id).first()


def atualizar_feriado(
    feriado_id: int,
    db: Session,
    **kwargs
) -> Optional[Feriado]:
    """
    Atualiza um feriado.
    
    Args:
        feriado_id: ID do feriado
        db: Sessão do banco de dados
        **kwargs: Campos a atualizar
    
    Returns:
        Feriado atualizado ou None se não encontrado
    """
    feriado = db.query(Feriado).filter(Feriado.id == feriado_id).first()
    if not feriado:
        return None
    
    # Validações se tipo for alterado
    if 'tipo' in kwargs:
        tipo = kwargs['tipo']
        if tipo == 'estadual' and not kwargs.get('uf') and not feriado.uf:
            raise ValueError("UF é obrigatória para feriados estaduais")
        if tipo == 'municipal' and not kwargs.get('municipio_id') and not feriado.municipio_id:
            raise ValueError("Município é obrigatório para feriados municipais")
    
    for key, value in kwargs.items():
        if hasattr(feriado, key):
            if key == 'uf' and value:
                setattr(feriado, key, value.upper())
            else:
                setattr(feriado, key, value)
    
    db.commit()
    db.refresh(feriado)
    return feriado


def deletar_feriado(feriado_id: int, db: Session) -> bool:
    """
    Deleta um feriado.
    
    Args:
        feriado_id: ID do feriado
        db: Sessão do banco de dados
    
    Returns:
        True se deletado, False se não encontrado
    """
    feriado = db.query(Feriado).filter(Feriado.id == feriado_id).first()
    if not feriado:
        return False
    
    db.delete(feriado)
    db.commit()
    return True


def obter_calendario_mes(
    ano: int,
    mes: int,
    municipio_id: Optional[int],
    db: Session
) -> List[Dict]:
    """
    Retorna informações sobre cada dia do mês para renderizar calendário.
    
    Args:
        ano: Ano
        mes: Mês (1-12)
        municipio_id: ID do município (None para apenas nacionais)
        db: Sessão do banco de dados
    
    Returns:
        Lista de dicts com {dia, dia_util, feriado, nome_feriado, fim_semana}
    """
    from calendar import monthrange
    from utils.prazos import eh_dia_util, eh_feriado, eh_fim_de_semana
    
    # Descobre quantos dias tem o mês
    _, num_dias = monthrange(ano, mes)
    
    # Lista feriados do mês
    data_inicio = date(ano, mes, 1)
    if mes == 12:
        data_fim = date(ano, 12, 31)
    else:
        data_fim = date(ano, mes, num_dias)
    
    feriados_mes = listar_feriados_por_periodo(data_inicio, data_fim, municipio_id, db)
    feriados_dict = {f.data: f.nome for f in feriados_mes}
    
    # Cria lista de dias
    dias = []
    for dia in range(1, num_dias + 1):
        data_dia = date(ano, mes, dia)
        eh_feriado_flag = data_dia in feriados_dict
        eh_fim_semana_flag = eh_fim_de_semana(data_dia)
        
        dias.append({
            "dia": dia,
            "data": data_dia.isoformat(),
            "dia_util": eh_dia_util(data_dia, municipio_id, db),
            "feriado": eh_feriado_flag,
            "nome_feriado": feriados_dict.get(data_dia),
            "fim_semana": eh_fim_semana_flag
        })
    
    return dias


def processar_feriados_recorrentes(ano_destino: int, db: Session) -> int:
    """
    Duplica feriados recorrentes para um ano específico.
    Útil para popular automaticamente feriados do próximo ano.
    
    Args:
        ano_destino: Ano para onde copiar os feriados
        db: Sessão do banco de dados
    
    Returns:
        Quantidade de feriados criados
    """
    # Busca feriados recorrentes de qualquer ano anterior
    feriados_recorrentes = db.query(Feriado).filter(
        Feriado.recorrente == True
    ).all()
    
    criados = 0
    for feriado_orig in feriados_recorrentes:
        # Monta a nova data no ano destino
        try:
            nova_data = date(ano_destino, feriado_orig.data.month, feriado_orig.data.day)
        except ValueError:
            # Caso de 29 de fevereiro em ano não bissexto
            continue
        
        # Verifica se já existe
        existe = db.query(Feriado).filter(
            Feriado.data == nova_data,
            Feriado.nome == feriado_orig.nome,
            Feriado.tipo == feriado_orig.tipo,
            Feriado.uf == feriado_orig.uf,
            Feriado.municipio_id == feriado_orig.municipio_id
        ).first()
        
        if not existe:
            novo_feriado = Feriado(
                data=nova_data,
                nome=feriado_orig.nome,
                tipo=feriado_orig.tipo,
                uf=feriado_orig.uf,
                municipio_id=feriado_orig.municipio_id,
                recorrente=True,
                criado_por=feriado_orig.criado_por
            )
            db.add(novo_feriado)
            criados += 1
    
    if criados > 0:
        db.commit()
    
    return criados
