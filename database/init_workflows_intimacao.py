"""
Script para inicializar tipos de tarefas, tipos de andamentos e workflows.
"""
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from database.database import SessionLocal, engine
from database.models import Base, TipoTarefa, TipoAndamento, WorkflowTemplate


def popular_tipos_tarefa(db: Session):
    """Popula tipos de tarefas principais."""
    print("Populando tipos de tarefas...")
    
    tipos = [
        {
            "nome": "Análise de Intimação",
            "descricao_padrao": "Análise e classificação de intimação judicial recebida"
        },
        {
            "nome": "Petição",
            "descricao_padrao": "Elaboração de petição para protocolo judicial"
        },
        {
            "nome": "Recurso",
            "descricao_padrao": "Elaboração de recurso judicial"
        },
        {
            "nome": "Preparar Audiência",
            "descricao_padrao": "Preparação para audiência judicial"
        },
        {
            "nome": "Acompanhar Publicação",
            "descricao_padrao": "Acompanhamento de publicações no Diário Oficial"
        },
        {
            "nome": "Análise de Documentos",
            "descricao_padrao": "Análise técnica de documentos do processo"
        },
        {
            "nome": "Reunião com Cliente",
            "descricao_padrao": "Reunião para alinhamento com cliente"
        },
        {
            "nome": "Diligência Externa",
            "descricao_padrao": "Realização de diligência externa"
        },
    ]
    
    inseridos = 0
    existentes = 0
    
    for tipo_data in tipos:
        existe = db.query(TipoTarefa).filter(
            TipoTarefa.nome == tipo_data["nome"]
        ).first()
        
        if not existe:
            tipo = TipoTarefa(**tipo_data)
            db.add(tipo)
            inseridos += 1
        else:
            existentes += 1
    
    db.commit()
    print(f"  ✅ {inseridos} tipos de tarefa inseridos")
    if existentes > 0:
        print(f"  ℹ️  {existentes} tipos já existiam")


def popular_tipos_andamento(db: Session):
    """Popula tipos de andamentos."""
    print("\nPopulando tipos de andamentos...")
    
    tipos = [
        {
            "nome": "Decisão Interlocutória",
            "descricao_padrao": "Decisão interlocutória proferida pelo juiz"
        },
        {
            "nome": "Sentença",
            "descricao_padrao": "Sentença de mérito proferida"
        },
        {
            "nome": "Audiência Realizada",
            "descricao_padrao": "Registro de audiência realizada"
        },
        {
            "nome": "Petição Protocolada",
            "descricao_padrao": "Petição protocolada no processo"
        },
        {
            "nome": "Recurso Interposto",
            "descricao_padrao": "Recurso interposto no processo"
        },
        {
            "nome": "Juntada de Documentos",
            "descricao_padrao": "Documentos juntados aos autos"
        },
        {
            "nome": "Manifestação das Partes",
            "descricao_padrao": "Manifestação apresentada pelas partes"
        },
    ]
    
    inseridos = 0
    existentes = 0
    
    for tipo_data in tipos:
        existe = db.query(TipoAndamento).filter(
            TipoAndamento.nome == tipo_data["nome"]
        ).first()
        
        if not existe:
            tipo = TipoAndamento(**tipo_data)
            db.add(tipo)
            inseridos += 1
        else:
            existentes += 1
    
    db.commit()
    print(f"  ✅ {inseridos} tipos de andamento inseridos")
    if existentes > 0:
        print(f"  ℹ️  {existentes} tipos já existiam")


def popular_workflow_templates(db: Session):
    """Popula templates de workflow para cada tipo de tarefa."""
    print("\nPopulando templates de workflow...")
    
    # Workflow para Análise de Intimação
    tipo_intimacao = db.query(TipoTarefa).filter(
        TipoTarefa.nome == "Análise de Intimação"
    ).first()
    
    if tipo_intimacao:
        existe_wf = db.query(WorkflowTemplate).filter(
            WorkflowTemplate.tipo_tarefa_id == tipo_intimacao.id
        ).first()
        
        if not existe_wf:
            workflow = WorkflowTemplate(
                tipo_tarefa_id=tipo_intimacao.id,
                etapas=[
                    {
                        "nome": "analise_pendente",
                        "ordem": 1,
                        "acao_label": "Iniciar Análise",
                        "pode_criar_tarefa": False
                    },
                    {
                        "nome": "intimacao_classificada",
                        "ordem": 2,
                        "acao_label": "Classificar Intimação",
                        "pode_criar_tarefa": True
                    },
                    {
                        "nome": "concluido",
                        "ordem": 3,
                        "acao_label": "Concluir",
                        "pode_criar_tarefa": False
                    }
                ]
            )
            db.add(workflow)
            print(f"  ✅ Workflow criado para 'Análise de Intimação'")
    
    # Workflow para Petição
    tipo_peticao = db.query(TipoTarefa).filter(
        TipoTarefa.nome == "Petição"
    ).first()
    
    if tipo_peticao:
        existe_wf = db.query(WorkflowTemplate).filter(
            WorkflowTemplate.tipo_tarefa_id == tipo_peticao.id
        ).first()
        
        if not existe_wf:
            workflow = WorkflowTemplate(
                tipo_tarefa_id=tipo_peticao.id,
                etapas=[
                    {
                        "nome": "elaboracao",
                        "ordem": 1,
                        "acao_label": "Elaborar Petição",
                        "pode_criar_tarefa": False
                    },
                    {
                        "nome": "revisao",
                        "ordem": 2,
                        "acao_label": "Revisar",
                        "pode_criar_tarefa": False
                    },
                    {
                        "nome": "aprovado",
                        "ordem": 3,
                        "acao_label": "Aprovar",
                        "pode_criar_tarefa": False
                    },
                    {
                        "nome": "protocolado",
                        "ordem": 4,
                        "acao_label": "Protocolar",
                        "pode_criar_tarefa": True
                    },
                    {
                        "nome": "concluido",
                        "ordem": 5,
                        "acao_label": "Concluir",
                        "pode_criar_tarefa": False
                    }
                ]
            )
            db.add(workflow)
            print(f"  ✅ Workflow criado para 'Petição'")
    
    # Workflow para Recurso
    tipo_recurso = db.query(TipoTarefa).filter(
        TipoTarefa.nome == "Recurso"
    ).first()
    
    if tipo_recurso:
        existe_wf = db.query(WorkflowTemplate).filter(
            WorkflowTemplate.tipo_tarefa_id == tipo_recurso.id
        ).first()
        
        if not existe_wf:
            workflow = WorkflowTemplate(
                tipo_tarefa_id=tipo_recurso.id,
                etapas=[
                    {
                        "nome": "elaboracao",
                        "ordem": 1,
                        "acao_label": "Elaborar Recurso",
                        "pode_criar_tarefa": False
                    },
                    {
                        "nome": "revisao",
                        "ordem": 2,
                        "acao_label": "Revisar",
                        "pode_criar_tarefa": False
                    },
                    {
                        "nome": "aprovado",
                        "ordem": 3,
                        "acao_label": "Aprovar",
                        "pode_criar_tarefa": False
                    },
                    {
                        "nome": "protocolado",
                        "ordem": 4,
                        "acao_label": "Protocolar",
                        "pode_criar_tarefa": True
                    },
                    {
                        "nome": "concluido",
                        "ordem": 5,
                        "acao_label": "Concluir",
                        "pode_criar_tarefa": False
                    }
                ]
            )
            db.add(workflow)
            print(f"  ✅ Workflow criado para 'Recurso'")
    
    # Workflow genérico para outras tarefas
    outros_tipos = db.query(TipoTarefa).filter(
        ~TipoTarefa.nome.in_(["Análise de Intimação", "Petição", "Recurso"])
    ).all()
    
    for tipo in outros_tipos:
        existe_wf = db.query(WorkflowTemplate).filter(
            WorkflowTemplate.tipo_tarefa_id == tipo.id
        ).first()
        
        if not existe_wf:
            workflow = WorkflowTemplate(
                tipo_tarefa_id=tipo.id,
                etapas=[
                    {
                        "nome": "pendente",
                        "ordem": 1,
                        "acao_label": "Iniciar",
                        "pode_criar_tarefa": False
                    },
                    {
                        "nome": "em_andamento",
                        "ordem": 2,
                        "acao_label": "Em Andamento",
                        "pode_criar_tarefa": True
                    },
                    {
                        "nome": "concluido",
                        "ordem": 3,
                        "acao_label": "Concluir",
                        "pode_criar_tarefa": False
                    }
                ]
            )
            db.add(workflow)
    
    db.commit()
    print(f"  ✅ Workflows genéricos criados para demais tarefas")


def main():
    """Função principal para executar o script."""
    print("=" * 60)
    print("INICIALIZAÇÃO DE TIPOS E WORKFLOWS")
    print("=" * 60)
    print()
    
    # Cria as tabelas se não existirem
    print("Verificando estrutura do banco de dados...")
    Base.metadata.create_all(bind=engine)
    print("✅ Estrutura verificada.")
    print()
    
    # Cria sessão e popula
    db = SessionLocal()
    try:
        popular_tipos_tarefa(db)
        popular_tipos_andamento(db)
        popular_workflow_templates(db)
        
        # Estatísticas finais
        print()
        print("📊 Estatísticas:")
        print(f"   Tipos de Tarefa: {db.query(TipoTarefa).count()}")
        print(f"   Tipos de Andamento: {db.query(TipoAndamento).count()}")
        print(f"   Workflows: {db.query(WorkflowTemplate).count()}")
        
    finally:
        db.close()
    
    print()
    print("=" * 60)
    print("INICIALIZAÇÃO CONCLUÍDA")
    print("=" * 60)


if __name__ == "__main__":
    main()
