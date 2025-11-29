from database.models import Tarefa, Processo, Cliente, Municipio
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, date
from typing import List, Optional, Dict
import json
 
def criar_tarefa(db: Session, processo_id: int, tipo_tarefa_id: int, descricao_complementar: str | None = None, prazo: date | None = None, responsavel_id: int | None = None, status: str = "pendente"):
    """Cria uma nova tarefa no banco de dados."""
    t = Tarefa(
        processo_id=processo_id,
        tipo_tarefa_id=tipo_tarefa_id,
        descricao_complementar=descricao_complementar,
        prazo=prazo,
        responsavel_id=responsavel_id,
        status=status,
        criado_em=datetime.utcnow(),
        atualizado_em=datetime.utcnow()
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return t
 
def listar_tarefas(db: Session):
    """Lista todas as tarefas (usado pela API principal)."""
    return db.query(Tarefa).all()

def listar_tarefas_do_processo(processo_id: int, db: Session):
    return db.query(Tarefa).filter(Tarefa.processo_id == processo_id).order_by(Tarefa.prazo).all()


def listar_tarefas_gerais(db: Session):
    return db.query(Tarefa).filter(Tarefa.processo_id == None).order_by(Tarefa.prazo).all()


def listar_tarefas_por_responsavel(responsavel_id: int, db: Session):
    return db.query(Tarefa).filter(Tarefa.responsavel_id == responsavel_id).order_by(Tarefa.prazo).all()


def buscar_tarefa(tarefa_id: int, db: Session):
    return db.query(Tarefa).filter(Tarefa.id == tarefa_id).first()


def atualizar_tarefa(tarefa_id: int, db: Session, **kwargs):
    t = db.query(Tarefa).filter(Tarefa.id == tarefa_id).first()
    if not t:
        return None
    for k, v in kwargs.items():
        if hasattr(t, k):
            setattr(t, k, v)
    t.atualizado_em = datetime.utcnow()
    db.commit()
    db.refresh(t)
    return t


def deletar_tarefa(tarefa_id: int, db: Session):
    t = db.query(Tarefa).filter(Tarefa.id == tarefa_id).first()
    if not t:
        return False
    db.delete(t)
    db.commit()
    return True


def listar_tarefas_por_prazo(inicio: date, fim: date, db: Session):
    return db.query(Tarefa).filter(Tarefa.prazo >= inicio, Tarefa.prazo <= fim).all()


# ==================== NOVAS FUNÇÕES DE WORKFLOW ====================

def avancar_workflow_tarefa(
    tarefa_id: int,
    nova_etapa: str,
    usuario_id: int,
    usuario_nome: str,
    acao: str,
    db: Session
) -> Optional[Tarefa]:
    """
    Avança o workflow de uma tarefa para nova etapa.
    Valida se o usuário é o responsável pela tarefa.
    
    Args:
        tarefa_id: ID da tarefa
        nova_etapa: Nome da nova etapa do workflow
        usuario_id: ID do usuário executando a ação
        usuario_nome: Nome do usuário
        acao: Descrição da ação realizada
        db: Sessão do banco de dados
    
    Returns:
        Tarefa atualizada ou None se validação falhar
    """
    tarefa = db.query(Tarefa).filter(Tarefa.id == tarefa_id).first()
    if not tarefa:
        return None
    
    # Valida se usuário é o responsável
    if tarefa.responsavel_id != usuario_id:
        raise PermissionError("Apenas o responsável pela tarefa pode avançar o workflow")
    
    # Atualiza etapa
    etapa_anterior = tarefa.etapa_workflow_atual
    tarefa.etapa_workflow_atual = nova_etapa
    
    # Adiciona entrada no histórico
    historico = tarefa.workflow_historico or []
    historico.append({
        "etapa_anterior": etapa_anterior,
        "etapa_nova": nova_etapa,
        "usuario_id": usuario_id,
        "usuario_nome": usuario_nome,
        "timestamp": datetime.utcnow().isoformat(),
        "acao": acao
    })
    tarefa.workflow_historico = historico
    
    tarefa.atualizado_em = datetime.utcnow()
    db.commit()
    db.refresh(tarefa)
    return tarefa


def validar_pode_avancar_workflow(tarefa_id: int, usuario_id: int, db: Session) -> bool:
    """
    Valida se um usuário pode avançar o workflow de uma tarefa.
    
    Args:
        tarefa_id: ID da tarefa
        usuario_id: ID do usuário
        db: Sessão do banco de dados
    
    Returns:
        True se pode avançar, False caso contrário
    """
    tarefa = db.query(Tarefa).filter(Tarefa.id == tarefa_id).first()
    if not tarefa:
        return False
    
    return tarefa.responsavel_id == usuario_id


def criar_tarefa_derivada(
    tarefa_origem_id: int,
    tipo_tarefa_id: int,
    processo_id: int,
    responsavel_id: int,
    prazo_administrativo: Optional[date],
    prazo_fatal: Optional[date],
    descricao_complementar: Optional[str],
    db: Session
) -> Tarefa:
    """
    Cria uma tarefa derivada de outra tarefa.
    NÃO herda o responsável da tarefa origem.
    
    Args:
        tarefa_origem_id: ID da tarefa que originou esta
        tipo_tarefa_id: Tipo da nova tarefa
        processo_id: ID do processo
        responsavel_id: ID do responsável (fornecido, não herdado)
        prazo_administrativo: Prazo administrativo
        prazo_fatal: Prazo fatal
        descricao_complementar: Descrição adicional
        db: Sessão do banco de dados
    
    Returns:
        Tarefa derivada criada
    """
    tarefa = Tarefa(
        processo_id=processo_id,
        tipo_tarefa_id=tipo_tarefa_id,
        tarefa_origem_id=tarefa_origem_id,
        responsavel_id=responsavel_id,
        prazo_administrativo=prazo_administrativo,
        prazo_fatal=prazo_fatal,
        prazo=prazo_fatal,  # Mantém compatibilidade
        descricao_complementar=descricao_complementar,
        etapa_workflow_atual="pendente",
        status="pendente",
        criado_em=datetime.utcnow(),
        atualizado_em=datetime.utcnow()
    )
    
    db.add(tarefa)
    db.commit()
    db.refresh(tarefa)
    return tarefa


def listar_tarefas_derivadas(tarefa_id: int, db: Session, recursivo: bool = False) -> List[Tarefa]:
    """
    Lista tarefas derivadas de uma tarefa.
    
    Args:
        tarefa_id: ID da tarefa origem
        db: Sessão do banco de dados
        recursivo: Se True, retorna todas tarefas na cadeia de derivação
    
    Returns:
        Lista de tarefas derivadas
    """
    if not recursivo:
        return db.query(Tarefa).filter(Tarefa.tarefa_origem_id == tarefa_id).all()
    
    # Busca recursiva
    derivadas = []
    fila = [tarefa_id]
    visitados = set()
    
    while fila:
        atual_id = fila.pop(0)
        if atual_id in visitados:
            continue
        
        visitados.add(atual_id)
        filhas = db.query(Tarefa).filter(Tarefa.tarefa_origem_id == atual_id).all()
        
        for tarefa in filhas:
            derivadas.append(tarefa)
            fila.append(tarefa.id)
    
    return derivadas


def listar_tarefas_com_filtros(
    db: Session,
    tipo_tarefa_id: Optional[int] = None,
    processo_id: Optional[int] = None,
    cliente_id: Optional[int] = None,
    classe: Optional[str] = None,
    esfera_justica: Optional[str] = None,
    municipio_id: Optional[int] = None,
    uf: Optional[str] = None,
    responsavel_id: Optional[int] = None,
    status: Optional[str] = None,
    prazo_vencido: bool = False,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None
) -> List[Tarefa]:
    """
    Lista tarefas com filtros avançados incluindo dados de processo/cliente.
    
    Args:
        db: Sessão do banco de dados
        tipo_tarefa_id: Filtro por tipo de tarefa
        processo_id: Filtro por processo específico
        cliente_id: Filtro por cliente
        classe: Filtro por classe processual
        esfera_justica: Filtro por esfera de justiça
        municipio_id: Filtro por município
        uf: Filtro por UF
        responsavel_id: Filtro por responsável
        status: Filtro por status
        prazo_vencido: Se True, apenas tarefas com prazo fatal vencido
        data_inicio: Data inicial de criação
        data_fim: Data final de criação
    
    Returns:
        Lista de tarefas filtradas
    """
    query = db.query(Tarefa).join(
        Processo, Tarefa.processo_id == Processo.id, isouter=True
    ).join(
        Cliente, Processo.cliente_id == Cliente.id, isouter=True
    ).join(
        Municipio, Processo.municipio_id == Municipio.id, isouter=True
    ).options(
        joinedload(Tarefa.processo),
        joinedload(Tarefa.tipo_tarefa),
        joinedload(Tarefa.responsavel)
    )
    
    # Aplicar filtros
    if tipo_tarefa_id:
        query = query.filter(Tarefa.tipo_tarefa_id == tipo_tarefa_id)
    
    if processo_id:
        query = query.filter(Tarefa.processo_id == processo_id)
    
    if cliente_id:
        query = query.filter(Processo.cliente_id == cliente_id)
    
    if classe:
        query = query.filter(Processo.classe == classe)
    
    if esfera_justica:
        query = query.filter(Processo.esfera_justica == esfera_justica)
    
    if municipio_id:
        query = query.filter(Processo.municipio_id == municipio_id)
    
    if uf:
        query = query.filter(Municipio.uf == uf.upper())
    
    if responsavel_id:
        query = query.filter(Tarefa.responsavel_id == responsavel_id)
    
    if status:
        query = query.filter(Tarefa.status == status)
    
    if prazo_vencido:
        hoje = date.today()
        query = query.filter(Tarefa.prazo_fatal < hoje)
    
    if data_inicio:
        query = query.filter(Tarefa.criado_em >= data_inicio)
    
    if data_fim:
        query = query.filter(Tarefa.criado_em <= data_fim)
    
    # Ordena por prazo fatal (mais urgentes primeiro)
    return query.order_by(Tarefa.prazo_fatal.asc()).all()


def obter_estatisticas_tarefas(db: Session) -> dict:
    """
    Retorna estatísticas gerais sobre tarefas.
    
    Returns:
        Dict com total, por status, vencidas, próximas a vencer
    """
    from datetime import timedelta
    
    hoje = date.today()
    proximos_7_dias = hoje + timedelta(days=7)
    
    total = db.query(Tarefa).count()
    
    # Contagem por status
    por_status = {}
    for status in ['Pendente', 'Em Andamento', 'Concluída', 'Cancelada']:
        por_status[status] = db.query(Tarefa).filter(Tarefa.status == status).count()
    
    # Tarefas vencidas (não concluídas com prazo fatal passado)
    vencidas = db.query(Tarefa).filter(
        Tarefa.status.notin_(['Concluída', 'Cancelada']),
        Tarefa.prazo_fatal < hoje
    ).count()
    
    # Tarefas próximas a vencer (próximos 7 dias)
    proximas_vencer = db.query(Tarefa).filter(
        Tarefa.status.notin_(['Concluída', 'Cancelada']),
        Tarefa.prazo_fatal >= hoje,
        Tarefa.prazo_fatal <= proximos_7_dias
    ).count()
    
    # Tarefas por tipo
    por_tipo = db.query(
        TipoTarefa.nome,
        func.count(Tarefa.id).label('quantidade')
    ).join(
        TipoTarefa, Tarefa.tipo_tarefa_id == TipoTarefa.id
    ).group_by(TipoTarefa.nome).all()
    
    return {
        'total': total,
        'por_status': por_status,
        'vencidas': vencidas,
        'proximas_vencer': proximas_vencer,
        'por_tipo': [{'tipo': t[0], 'quantidade': t[1]} for t in por_tipo]
    }


def obter_metricas_responsavel(db: Session) -> List[dict]:
    """
    Retorna métricas de tarefas por responsável.
    
    Returns:
        Lista com nome, total de tarefas, concluídas, taxa de conclusão
    """
    from models import Usuario
    
    usuarios = db.query(Usuario).all()
    metricas = []
    
    for usuario in usuarios:
        total = db.query(Tarefa).filter(Tarefa.responsavel_id == usuario.id).count()
        concluidas = db.query(Tarefa).filter(
            Tarefa.responsavel_id == usuario.id,
            Tarefa.status == 'Concluída'
        ).count()
        
        pendentes = db.query(Tarefa).filter(
            Tarefa.responsavel_id == usuario.id,
            Tarefa.status == 'Pendente'
        ).count()
        
        em_andamento = db.query(Tarefa).filter(
            Tarefa.responsavel_id == usuario.id,
            Tarefa.status == 'Em Andamento'
        ).count()
        
        taxa_conclusao = (concluidas / total * 100) if total > 0 else 0
        
        metricas.append({
            'responsavel': usuario.nome,
            'responsavel_id': usuario.id,
            'total': total,
            'concluidas': concluidas,
            'pendentes': pendentes,
            'em_andamento': em_andamento,
            'taxa_conclusao': round(taxa_conclusao, 2)
        })
    
    return sorted(metricas, key=lambda x: x['total'], reverse=True)


def obter_tempo_medio_por_tipo(db: Session) -> List[dict]:
    """
    Calcula tempo médio de conclusão por tipo de tarefa.
    
    Returns:
        Lista com tipo, tempo médio em dias, quantidade de tarefas concluídas
    """
    # Busca tarefas concluídas com datas
    tarefas_concluidas = db.query(Tarefa).filter(
        Tarefa.status == 'Concluída',
        Tarefa.criado_em.isnot(None),
        Tarefa.atualizado_em.isnot(None)
    ).options(joinedload(Tarefa.tipo_tarefa)).all()
    
    # Agrupa por tipo e calcula média
    tempos_por_tipo = {}
    for tarefa in tarefas_concluidas:
        tipo_nome = tarefa.tipo_tarefa.nome if tarefa.tipo_tarefa else 'Sem tipo'
        
        # Calcula dias entre criação e conclusão
        dias = (tarefa.atualizado_em - tarefa.criado_em).days
        
        if tipo_nome not in tempos_por_tipo:
            tempos_por_tipo[tipo_nome] = []
        tempos_por_tipo[tipo_nome].append(dias)
    
    # Calcula médias
    resultado = []
    for tipo, dias_lista in tempos_por_tipo.items():
        media = sum(dias_lista) / len(dias_lista)
        resultado.append({
            'tipo': tipo,
            'tempo_medio_dias': round(media, 1),
            'quantidade_concluidas': len(dias_lista)
        })
    
    return sorted(resultado, key=lambda x: x['quantidade_concluidas'], reverse=True)
