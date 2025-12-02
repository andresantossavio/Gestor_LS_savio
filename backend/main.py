from fastapi import FastAPI, Depends, HTTPException, APIRouter, Query, Body, Path
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path as PathLib
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import extract, func
from typing import Optional, List
from database.database import SessionLocal, engine, Base
from database import crud_clientes, crud_processos, crud_tarefas, crud_andamentos, crud_anexos, crud_pagamentos, crud_usuarios, crud_contabilidade, crud_municipios, crud_feriados, crud_plano_contas, models # Import models first
from .import_contabilidade import carregar_csv_contabilidade
from backend import schemas # Then import schemas
from backend import config_data # Import config data
from utils import prazos, exportacao  # Import utils
from datetime import date as date_type, datetime
import time  # Add this import for timing

# Ensure DB tables exist (uses existing SQLAlchemy Base)
# This needs to be run before the app is fully defined
Base.metadata.create_all(bind=engine)

app = FastAPI(title="GESTOR_LS API")

# Routers
api_router = APIRouter(prefix="/api")
config_router = APIRouter(prefix="/api/config")


# --- Config Endpoints ---
@config_router.get("/ufs", response_model=list[str])
def get_ufs():
    return config_data.UFS

@config_router.get("/tipos", response_model=list[str])
def get_tipos():
    return config_data.TIPOS_PROCESSO

@config_router.get("/categorias", response_model=list[str])
def get_categorias():
    return config_data.CATEGORIAS_PROCESSO

@config_router.get("/tribunais", response_model=list[str])
def get_tribunais():
    return config_data.TRIBUNAIS

@config_router.get("/esferas", response_model=list[str])
def get_esferas():
    return config_data.ESFERAS_JUSTICA

@config_router.get("/classes", response_model=dict[str, list[str]])
def get_classes():
    return config_data.CLASSES_JURIDICAS

@config_router.get("/ritos", response_model=dict[str, list[str]])
def get_ritos():
    return config_data.RITOS


# Enable CORS for local development and frontend app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@api_router.get("/clientes", response_model=list[schemas.Cliente])
def listar_clientes(db: Session = Depends(get_db)):
    return crud_clientes.listar_clientes(db)


@api_router.get("/clientes/{cliente_id}", response_model=schemas.Cliente)
def buscar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = crud_clientes.buscar_cliente_por_id(cliente_id, db)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return cliente


@api_router.post("/clientes", response_model=schemas.Cliente)
def criar_cliente(cliente: schemas.ClienteCreate, db: Session = Depends(get_db)):
    # Criar dict apenas com os campos que foram fornecidos (não None)
    dados = {k: v for k, v in cliente.model_dump().items() if v is not None}
    c = crud_clientes.criar_cliente(db, **dados)
    if not c:
        raise HTTPException(status_code=400, detail="Erro ao criar cliente")
    return c


@api_router.put("/clientes/{cliente_id}", response_model=schemas.Cliente)
def atualizar_cliente(cliente_id: int, cliente: schemas.ClienteUpdate, db: Session = Depends(get_db)):
    # Criar dict apenas com os campos que foram fornecidos (não None)
    dados = {k: v for k, v in cliente.model_dump().items() if v is not None}
    print(f"DEBUG - Atualizando cliente {cliente_id} com dados: {dados}")
    c = crud_clientes.atualizar_cliente(cliente_id, db, **dados)
    if not c:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return c


@api_router.delete("/clientes/{cliente_id}")
def deletar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    crud_clientes.deletar_cliente(cliente_id, db)
    return {"status": "ok"}

# ---------------- Contabilidade ----------------
from fastapi import UploadFile, File
from typing import List

# Endpoints de import CSV comentados (substituídos por cadastro manual de Entradas)
# @api_router.post("/contabilidade/import", response_model=List[dict])
# def import_contabilidade(file: UploadFile = File(...), db: Session = Depends(get_db)):
#     ...

# @api_router.get("/contabilidade/recebimentos", response_model=List[dict])
# def listar_recebimentos(db: Session = Depends(get_db)):
#     ...

# --- Sócios ---
@api_router.get("/contabilidade/socios", response_model=List[schemas.Socio])
def listar_socios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud_contabilidade.get_socios(db, skip=skip, limit=limit)

@api_router.post("/contabilidade/socios", response_model=schemas.Socio)
def criar_socio(socio: schemas.SocioCreate, db: Session = Depends(get_db)):
    return crud_contabilidade.create_socio(db, socio)

@api_router.put("/contabilidade/socios/{socio_id}", response_model=schemas.Socio)
def atualizar_socio(socio_id: int, socio: schemas.SocioUpdate, db: Session = Depends(get_db)):
    db_socio = crud_contabilidade.update_socio(db, socio_id, socio)
    if not db_socio:
        raise HTTPException(status_code=404, detail="Sócio não encontrado")
    return db_socio

@api_router.delete("/contabilidade/socios/{socio_id}")
def deletar_socio(socio_id: int, db: Session = Depends(get_db)):
    db_socio = crud_contabilidade.delete_socio(db, socio_id)
    if not db_socio:
        raise HTTPException(status_code=404, detail="Sócio não encontrado")
    return {"status": "ok"}

# --- Aportes de Capital ---
@api_router.post("/contabilidade/socios/{socio_id}/aportes")
def registrar_aporte(socio_id: int, aporte: schemas.AporteCapitalCreate, db: Session = Depends(get_db)):
    try:
        return crud_contabilidade.registrar_aporte_capital(
            db=db,
            socio_id=socio_id,
            valor=aporte.valor,
            data=aporte.data,
            forma=aporte.forma
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- Entradas ---
@api_router.get("/contabilidade/entradas", response_model=List[schemas.Entrada])
def listar_entradas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud_contabilidade.get_entradas(db, skip=skip, limit=limit)

@api_router.post("/contabilidade/entradas", response_model=schemas.Entrada)
def criar_entrada(entrada: schemas.EntradaCreate, db: Session = Depends(get_db)):
    nova_entrada = crud_contabilidade.create_entrada(db, entrada)
    
    # Tentar criar lançamento contábil automaticamente
    try:
        crud_plano_contas.lancar_entrada_honorarios(db, nova_entrada.id)
    except Exception as e:
        print(f"⚠️  Erro ao criar lançamento contábil para entrada {nova_entrada.id}: {e}")
    
    # Gerar pagamentos pendentes automaticamente
    try:
        from utils.simples import calcular_receita_12_meses
        
        # Calcula receita 12 meses
        receita_12m = calcular_receita_12_meses(db, nova_entrada.data)
        
        # Busca sócios com percentuais
        socios_entrada = db.query(models.EntradaSocio).filter(
            models.EntradaSocio.entrada_id == nova_entrada.id
        ).all()
        
        administrador_id = None
        socios_data = []
        for se in socios_entrada:
            socio = db.query(models.Socio).filter(models.Socio.id == se.socio_id).first()
            if socio:
                # Identifica o administrador pela função
                is_admin = socio.funcao and "administrador" in socio.funcao.lower()
                if is_admin:
                    administrador_id = socio.id
                
                socios_data.append({
                    "id": socio.id,
                    "nome": socio.nome,
                    "percentual": se.percentual,
                    "funcao": socio.funcao,
                    "is_admin": is_admin
                })
        
        # NÃO GERAR PENDÊNCIAS AUTOMATICAMENTE POR ENTRADA
        # Pendências devem ser geradas consolidadas por mês via endpoint dedicado
        # /api/pagamentos-pendentes/gerar/{mes}/{ano}
    except Exception as e:
        print(f"⚠️  Erro ao processar entrada {nova_entrada.id}: {e}")
    
    return nova_entrada

@api_router.put("/contabilidade/entradas/{entrada_id}", response_model=schemas.Entrada)
def atualizar_entrada(entrada_id: int, entrada: schemas.EntradaCreate, db: Session = Depends(get_db)):
    db_entrada = crud_contabilidade.update_entrada(db, entrada_id, entrada)
    if not db_entrada:
        raise HTTPException(status_code=404, detail="Entrada não encontrada")
    return db_entrada

@api_router.delete("/contabilidade/entradas/{entrada_id}")
def deletar_entrada(entrada_id: int, db: Session = Depends(get_db)):
    db_entrada = crud_contabilidade.delete_entrada(db, entrada_id)
    if not db_entrada:
        raise HTTPException(status_code=404, detail="Entrada não encontrada")
    return {"status": "ok"}

# --- Despesas ---
@api_router.get("/contabilidade/despesas", response_model=List[schemas.Despesa])
def listar_despesas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud_contabilidade.get_despesas(db, skip=skip, limit=limit)

@api_router.post("/contabilidade/despesas", response_model=schemas.Despesa)
def criar_despesa(despesa: schemas.DespesaCreate, db: Session = Depends(get_db)):
    nova_despesa = crud_contabilidade.create_despesa(db, despesa)
    
    # Tentar criar lançamento contábil automaticamente
    try:
        crud_plano_contas.lancar_despesa(db, nova_despesa.id)
    except Exception as e:
        print(f"⚠️  Erro ao criar lançamento contábil para despesa {nova_despesa.id}: {e}")
    
    return nova_despesa

@api_router.put("/contabilidade/despesas/{despesa_id}", response_model=schemas.Despesa)
def atualizar_despesa(despesa_id: int, despesa: schemas.DespesaCreate, db: Session = Depends(get_db)):
    db_despesa = crud_contabilidade.update_despesa(db, despesa_id, despesa)
    if not db_despesa:
        raise HTTPException(status_code=404, detail="Despesa não encontrada")
    return db_despesa

@api_router.delete("/contabilidade/despesas/{despesa_id}")
def deletar_despesa(despesa_id: int, db: Session = Depends(get_db)):
    db_despesa = crud_contabilidade.delete_despesa(db, despesa_id)
    if not db_despesa:
        raise HTTPException(status_code=404, detail="Despesa não encontrada")
    return {"status": "ok"}

# --- DRE ---
@api_router.get("/contabilidade/dre")
def listar_dre_ano(year: int, calcular_tempo_real: bool = False, db: Session = Depends(get_db)):
    """Retorna DRE dos 12 meses do ano especificado."""
    from utils.datas import meses_do_ano, inicio_do_mes, fim_do_mes, ultimos_12_meses
    from utils.simples import calcular_faixa_simples, calcular_imposto_simples
    from sqlalchemy import func
    
    meses = meses_do_ano(year)
    
    resultado = []
    for mes in meses:
        dre = crud_contabilidade.get_dre_mensal(db, mes)
        
        # Se está consolidado, retornar dados consolidados
        if dre and dre.consolidado:
            resultado.append({
                "mes": dre.mes,
                "receita_bruta": dre.receita_bruta,
                "receita_12m": dre.receita_12m,
                "aliquota": dre.aliquota,
                "aliquota_efetiva": dre.aliquota_efetiva,
                "deducao": dre.deducao,
                "imposto": dre.imposto,
                "pro_labore": dre.pro_labore,
                "inss_patronal": dre.inss_patronal,
                "inss_pessoal": dre.inss_pessoal,
                "inss_total": (dre.inss_patronal + dre.inss_pessoal),
                "despesas_gerais": dre.despesas_gerais,
                "lucro_liquido": dre.lucro_liquido,
                "reserva_10p": dre.reserva_10p,
                "consolidado": True
            })
        # Se não está consolidado e foi pedido cálculo em tempo real
        elif calcular_tempo_real:
            inicio = inicio_do_mes(mes)
            fim = fim_do_mes(mes)
            
            # Calcular receita bruta do mês
            receita_bruta = db.query(func.sum(models.Entrada.valor)).filter(
                models.Entrada.data >= inicio,
                models.Entrada.data <= fim
            ).scalar() or 0.0
            
            # Calcular receita acumulada 12 meses
            meses_12 = ultimos_12_meses(mes)
            receita_12m = 0.0
            for mes_ant in meses_12:
                inicio_ant = inicio_do_mes(mes_ant)
                fim_ant = fim_do_mes(mes_ant)
                receita_mes_ant = db.query(func.sum(models.Entrada.valor)).filter(
                    models.Entrada.data >= inicio_ant,
                    models.Entrada.data <= fim_ant
                ).scalar() or 0.0
                receita_12m += receita_mes_ant
            
            # Calcular faixa Simples e alíquotas
            try:
                aliquota, deducao, aliquota_efetiva = calcular_faixa_simples(receita_12m, inicio, db)
            except (ValueError, Exception):
                aliquota = 0.045  # 4.5% primeira faixa como padrão
                deducao = 0.0
                aliquota_efetiva = 0.0
            
            # Calcular imposto do mês
            imposto = calcular_imposto_simples(receita_bruta, aliquota_efetiva)
            
            # Calcular despesas gerais do mês
            despesas_gerais = db.query(func.sum(models.Despesa.valor)).filter(
                models.Despesa.data >= inicio,
                models.Despesa.data <= fim
            ).scalar() or 0.0
            
            # Calcular lucro bruto (antes de pró-labore e INSS)
            lucro_bruto = receita_bruta - imposto - despesas_gerais
            
            # Encontrar sócio administrador e seu percentual de contribuição
            admin_socio = db.query(models.Socio).filter(
                models.Socio.funcao.ilike('%administrador%')
            ).first()
            
            percentual_contrib_admin = 100.0  # Default se não tiver sócio admin
            
            if admin_socio:
                # Calcular contribuição do admin no mês
                entradas_mes = db.query(models.Entrada).filter(
                    models.Entrada.data >= inicio,
                    models.Entrada.data <= fim
                ).all()
                
                contribuicao_admin = 0.0
                faturamento_total = 0.0
                
                for entrada in entradas_mes:
                    faturamento_total += float(entrada.valor or 0)
                    entrada_socio = db.query(models.EntradaSocio).filter(
                        models.EntradaSocio.entrada_id == entrada.id,
                        models.EntradaSocio.socio_id == admin_socio.id
                    ).first()
                    
                    if entrada_socio:
                        percentual = float(entrada_socio.percentual or 0)
                        contribuicao_admin += float(entrada.valor or 0) * (percentual / 100)
                
                if faturamento_total > 0:
                    percentual_contrib_admin = (contribuicao_admin / faturamento_total) * 100
            
            # Calcular pró-labore e INSS de forma iterativa
            config = crud_contabilidade.get_configuracao(db)
            salario_minimo = config.salario_minimo if config else 1518.0
            pro_labore, inss_patronal, inss_pessoal, lucro_liquido = crud_contabilidade.calcular_pro_labore_iterativo(
                lucro_bruto, 
                percentual_contrib_admin,
                salario_minimo
            )
            
            # Calcular reserva 10%
            reserva_10p = lucro_liquido * 0.10
            
            resultado.append({
                "mes": mes,
                "receita_bruta": receita_bruta,
                "receita_12m": receita_12m,
                "aliquota": aliquota,
                "aliquota_efetiva": aliquota_efetiva,
                "deducao": deducao,
                "imposto": imposto,
                "pro_labore": pro_labore,
                "inss_patronal": inss_patronal,
                "inss_pessoal": inss_pessoal,
                "inss_total": (inss_patronal + inss_pessoal),
                "despesas_gerais": despesas_gerais,
                "lucro_liquido": lucro_liquido,
                "reserva_10p": reserva_10p,
                "consolidado": False
            })
        else:
            # Se não consolidado e não pediu cálculo, retornar estrutura vazia
            resultado.append({
                "mes": mes,
                "receita_bruta": 0.0,
                "receita_12m": 0.0,
                "aliquota": 0.0,
                "aliquota_efetiva": 0.0,
                "deducao": 0.0,
                "imposto": 0.0,
                "pro_labore": 0.0,
                "inss_patronal": 0.0,
                "inss_pessoal": 0.0,
                "inss_total": 0.0,
                "despesas_gerais": 0.0,
                "lucro_liquido": 0.0,
                "reserva_10p": 0.0,
                "consolidado": False
            })
    
    return resultado


# --- Pró‑Labore (por sócio administrador) ---
@api_router.get("/contabilidade/pro-labore/{socio_id}")
def obter_pro_labore_socio(
    socio_id: int,
    year: int = Query(..., ge=2000),
    db: Session = Depends(get_db)
):
    """Retorna, mês a mês, o pró‑labore do administrador alinhado à DRE consolidada.

    Estrutura de resposta compatível com a página `ProLabore.jsx`:
    {
      meses: [
        {
          ano, mes, faturamento_total, contribuicao_socio, percentual_contribuicao,
          pro_labore_bruto, inss_pessoal, inss_patronal, pro_labore_liquido,
          lucro_liquido, lucro_final_socio
        }, ...
      ]
    }
    """
    from utils.datas import meses_do_ano, inicio_do_mes, fim_do_mes, ultimos_12_meses
    from utils.simples import calcular_faixa_simples, calcular_imposto_simples

    socio = crud_contabilidade.get_socio(db, socio_id)
    if not socio:
        raise HTTPException(status_code=404, detail="Sócio não encontrado")
    if not (socio.funcao and 'administrador' in socio.funcao.lower()):
        # Esta API está focada no administrador (pró‑labore)
        raise HTTPException(status_code=400, detail="Endpoint disponível apenas para sócio administrador")

    meses = meses_do_ano(year)
    saida = []

    for mes_str in meses:
        # Consolidado primeiro
        dre = crud_contabilidade.get_dre_mensal(db, mes_str)

        inicio = inicio_do_mes(mes_str)
        fim = fim_do_mes(mes_str)

        # Faturamento total do mês e contribuição do sócio nas entradas
        entradas_mes = db.query(models.Entrada).filter(
            models.Entrada.data >= inicio,
            models.Entrada.data <= fim
        ).all()

        faturamento_total = sum(float(e.valor or 0) for e in entradas_mes)
        contribuicao_socio = 0.0
        for e in entradas_mes:
            es = db.query(models.EntradaSocio).filter(
                models.EntradaSocio.entrada_id == e.id,
                models.EntradaSocio.socio_id == socio_id
            ).first()
            if es:
                contribuicao_socio += float(e.valor or 0) * (float(es.percentual or 0) / 100.0)

        percentual_contrib = (contribuicao_socio / faturamento_total * 100.0) if faturamento_total > 0 else 0.0

        if dre and dre.consolidado:
            pro_labore_bruto = float(dre.pro_labore or 0)
            inss_patronal = float(dre.inss_patronal or 0)
            inss_pessoal = float(dre.inss_pessoal or 0)
            lucro_liquido = float(dre.lucro_liquido or 0)
        else:
            # Cálculo em tempo real replicando o de DRE
            # Receita do mês
            receita_bruta = db.query(func.sum(models.Entrada.valor)).filter(
                models.Entrada.data >= inicio,
                models.Entrada.data <= fim
            ).scalar() or 0.0

            # Receita acumulada 12 meses
            receita_12m = 0.0
            for m12 in ultimos_12_meses(mes_str):
                i12 = inicio_do_mes(m12)
                f12 = fim_do_mes(m12)
                receita_12m += db.query(func.sum(models.Entrada.valor)).filter(
                    models.Entrada.data >= i12,
                    models.Entrada.data <= f12
                ).scalar() or 0.0

            try:
                _, _, aliquota_efetiva = calcular_faixa_simples(receita_12m, inicio, db)
            except Exception:
                aliquota_efetiva = 0.0

            imposto = calcular_imposto_simples(receita_bruta, aliquota_efetiva)
            despesas_gerais = db.query(func.sum(models.Despesa.valor)).filter(
                models.Despesa.data >= inicio,
                models.Despesa.data <= fim
            ).scalar() or 0.0
            lucro_bruto = receita_bruta - imposto - despesas_gerais

            config = crud_contabilidade.get_configuracao(db)
            salario_minimo = config.salario_minimo if config else 1518.0
            pro_labore_bruto, inss_patronal, inss_pessoal, lucro_liquido = crud_contabilidade.calcular_pro_labore_iterativo(
                lucro_bruto, percentual_contrib, salario_minimo
            )

        pro_labore_liquido = pro_labore_bruto * 0.89
        lucro_final_socio = pro_labore_liquido  # para admin

        saida.append({
            "ano": int(mes_str.split('-')[0]),
            "mes": int(mes_str.split('-')[1]),
            "faturamento_total": round(faturamento_total, 2),
            "contribuicao_socio": round(contribuicao_socio, 2),
            "percentual_contribuicao": round(percentual_contrib, 2),
            "pro_labore_bruto": round(pro_labore_bruto, 2),
            "inss_pessoal": round(inss_pessoal, 2),
            "inss_patronal": round(inss_patronal, 2),
            "pro_labore_liquido": round(pro_labore_liquido, 2),
            "lucro_liquido": round(lucro_liquido, 2),
            "lucro_final_socio": round(lucro_final_socio, 2),
        })

    return {"socio_id": socio_id, "ano": year, "meses": saida}

@api_router.post("/contabilidade/dre/consolidar")
def consolidar_dre(mes: str, forcar: bool = False, db: Session = Depends(get_db)):
    """Consolida ou recalcula a DRE de um mês específico."""
    try:
        dre = crud_contabilidade.consolidar_dre_mes(db, mes, forcar_recalculo=forcar)
        return {
            "mes": dre.mes,
            "receita_bruta": dre.receita_bruta,
            "receita_12m": dre.receita_12m,
            "aliquota": dre.aliquota,
            "aliquota_efetiva": dre.aliquota_efetiva,
            "deducao": dre.deducao,
            "imposto": dre.imposto,
            "pro_labore": dre.pro_labore,
            "inss_patronal": dre.inss_patronal,
            "inss_pessoal": dre.inss_pessoal,
            "inss_total": (dre.inss_patronal + dre.inss_pessoal),
            "despesas_gerais": dre.despesas_gerais,
            "lucro_liquido": dre.lucro_liquido,
            "reserva_10p": dre.reserva_10p,
            "consolidado": dre.consolidado
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.delete("/contabilidade/dre/consolidar")
def desconsolidar_dre(mes: str, db: Session = Depends(get_db)):
    """Desconsolida um mês de DRE, permitindo recalcular posteriormente."""
    try:
        dre = crud_contabilidade.desconsolidar_dre_mes(db, mes)
        if not dre:
            raise HTTPException(status_code=404, detail=f"DRE do mês {mes} não encontrado")
        return {
            "mes": dre.mes,
            "consolidado": dre.consolidado,
            "message": f"Mês {mes} desconsolidado com sucesso"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.get("/contabilidade/dashboard-summary")
def obter_dashboard_summary(db: Session = Depends(get_db)):
    """
    Retorna um resumo dos dados contábeis para o dashboard.
    Inclui: balanço patrimonial, lucros e fundos, distribuição de sócios.
    """
    from sqlalchemy import func
    from datetime import datetime
    
    # Obter ano atual
    ano_atual = datetime.now().year
    
    # Buscar todos os DREs consolidados do ano atual
    dres = db.query(models.DREMensal).filter(
        models.DREMensal.mes.like(f"{ano_atual}-%"),
        models.DREMensal.consolidado == True
    ).all()
    
    # Somar lucros líquidos consolidados
    lucro_liquido_total = sum(dre.lucro_liquido for dre in dres)
    reserva_total = sum(dre.reserva_10p for dre in dres)
    pro_labore_total = sum(dre.pro_labore for dre in dres)
    
    # Buscar fundos
    fundo_reserva = crud_contabilidade.get_or_create_fundo(db, "Fundo de Reserva")
    fundo_investimento = crud_contabilidade.get_or_create_fundo(db, "Fundo de Investimento")
    
    # Calcular saldos dos sócios (simplificado - seria necessário implementar lógica de distribuição)
    socios = crud_contabilidade.get_socios(db)
    lucro_distribuivel = lucro_liquido_total - reserva_total - pro_labore_total
    
    saldo_socios = 0.0
    for socio in socios:
        perc = socio.percentual or 0.0
        # Aceita percentuais em decimal (0-1) ou inteiro (0-100)
        if perc > 1:
            perc = perc / 100.0
        saldo_socios += lucro_distribuivel * perc
    
    # Balanço Patrimonial
    ativo = saldo_socios + fundo_reserva.saldo + fundo_investimento.saldo
    passivo = 0.0  # Simplificado - não há passivos no sistema atual
    patrimonio_liquido = ativo - passivo
    
    # DRE Data (para gráfico)
    receita_bruta_total = sum(dre.receita_bruta for dre in dres)
    despesas_total = sum(dre.despesas_gerais for dre in dres)
    impostos_total = sum(dre.imposto for dre in dres)
    inss_total = sum((dre.inss_patronal + dre.inss_pessoal) for dre in dres)
    
    lucro_bruto = receita_bruta_total - despesas_total
    
    dre_data = [
        {"name": "Receita Bruta", "valor": receita_bruta_total},
        {"name": "Despesas", "valor": -despesas_total},
        {"name": "Lucro Bruto", "valor": lucro_bruto},
        {"name": "Impostos", "valor": -(impostos_total + inss_total)},
        {"name": "Lucro Líquido", "valor": lucro_liquido_total}
    ]
    
    # Distribuição de Sócios (para gráfico)
    distribuicao_socios = []
    for socio in socios:
        usuario = db.query(models.Usuario).filter(models.Usuario.id == socio.usuario_id).first()
        nome_socio = usuario.nome if usuario else f"Sócio {socio.id}"
        perc = socio.percentual or 0.0
        if perc > 1:
            perc = perc / 100.0
        valor_socio = lucro_distribuivel * perc
        distribuicao_socios.append({
            "name": nome_socio,
            "value": valor_socio
        })
    
    return {
        "balancoPatrimonial": {
            "ativo": ativo,
            "passivo": passivo,
            "patrimonioLiquido": patrimonio_liquido
        },
        "lucros": {
            "disponiveis": lucro_distribuivel,
            "distribuidos": saldo_socios,
            "fundoReserva": fundo_reserva.saldo,
            "proLabore": pro_labore_total
        },
        "dreData": dre_data,
        "distribuicaoSocios": distribuicao_socios,
        "ano": ano_atual
    }

# --- Faixas Simples ---
@api_router.get("/contabilidade/simples-faixas")
def listar_simples_faixas(db: Session = Depends(get_db)):
    """Lista todas as faixas do Simples Nacional configuradas."""
    faixas = crud_contabilidade.get_all_simples_faixas(db)
    return [{
        "id": f.id,
        "limite_superior": f.limite_superior,
        "aliquota": f.aliquota,
        "deducao": f.deducao,
        "vigencia_inicio": str(f.vigencia_inicio),
        "vigencia_fim": str(f.vigencia_fim) if f.vigencia_fim else None,
        "ordem": f.ordem
    } for f in faixas]

@api_router.post("/contabilidade/simples-faixas")
def criar_simples_faixa(faixa_data: dict, db: Session = Depends(get_db)):
    """Cria uma nova faixa do Simples."""
    from datetime import date as date_type
    from datetime import datetime
    
    # Converter strings de data
    if "vigencia_inicio" in faixa_data and isinstance(faixa_data["vigencia_inicio"], str):
        faixa_data["vigencia_inicio"] = datetime.strptime(faixa_data["vigencia_inicio"], "%Y-%m-%d").date()
    if "vigencia_fim" in faixa_data and faixa_data["vigencia_fim"] and isinstance(faixa_data["vigencia_fim"], str):
        faixa_data["vigencia_fim"] = datetime.strptime(faixa_data["vigencia_fim"], "%Y-%m-%d").date()
    
    faixa = crud_contabilidade.create_simples_faixa(db, faixa_data)
    return {
        "id": faixa.id,
        "limite_superior": faixa.limite_superior,
        "aliquota": faixa.aliquota,
        "deducao": faixa.deducao,
        "vigencia_inicio": str(faixa.vigencia_inicio),
        "vigencia_fim": str(faixa.vigencia_fim) if faixa.vigencia_fim else None,
        "ordem": faixa.ordem
    }

@api_router.put("/contabilidade/simples-faixas/{faixa_id}")
def atualizar_simples_faixa(faixa_id: int, faixa_data: dict, db: Session = Depends(get_db)):
    """Atualiza uma faixa do Simples."""
    from datetime import datetime
    
    # Converter strings de data
    if "vigencia_inicio" in faixa_data and isinstance(faixa_data["vigencia_inicio"], str):
        faixa_data["vigencia_inicio"] = datetime.strptime(faixa_data["vigencia_inicio"], "%Y-%m-%d").date()
    if "vigencia_fim" in faixa_data and faixa_data["vigencia_fim"] and isinstance(faixa_data["vigencia_fim"], str):
        faixa_data["vigencia_fim"] = datetime.strptime(faixa_data["vigencia_fim"], "%Y-%m-%d").date()
    
    faixa = crud_contabilidade.update_simples_faixa(db, faixa_id, faixa_data)
    if not faixa:
        raise HTTPException(status_code=404, detail="Faixa não encontrada")
    return {
        "id": faixa.id,
        "limite_superior": faixa.limite_superior,
        "aliquota": faixa.aliquota,
        "deducao": faixa.deducao,
        "vigencia_inicio": str(faixa.vigencia_inicio),
        "vigencia_fim": str(faixa.vigencia_fim) if faixa.vigencia_fim else None,
        "ordem": faixa.ordem
    }

@api_router.delete("/contabilidade/simples-faixas/{faixa_id}")
def deletar_simples_faixa(faixa_id: int, db: Session = Depends(get_db)):
    """Deleta uma faixa do Simples."""
    sucesso = crud_contabilidade.delete_simples_faixa(db, faixa_id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Faixa não encontrada")
    return {"status": "ok"}

@api_router.post("/contabilidade/simples-faixas/inicializar")
def inicializar_faixas_simples_endpoint(db: Session = Depends(get_db)):
    """Inicializa as faixas padrão do Simples Nacional (2025)."""
    from datetime import date
    from utils.simples import inicializar_faixas_simples
    
    try:
        data_vigencia = date(2025, 1, 1)
        inicializar_faixas_simples(db, data_vigencia)
        return {"status": "ok", "message": "Faixas do Simples inicializadas com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ===== PLANO DE CONTAS =====

@api_router.get("/contabilidade/plano-contas")
def listar_plano_contas(apenas_ativas: bool = True, db: Session = Depends(get_db)):
    """Lista todas as contas do plano de contas"""
    contas = crud_plano_contas.listar_plano_contas(db, apenas_ativas)
    return [
        {
            "id": c.id,
            "codigo": c.codigo,
            "descricao": c.descricao,
            "tipo": c.tipo,
            "natureza": c.natureza,
            "nivel": c.nivel,
            "pai_id": c.pai_id,
            "aceita_lancamento": c.aceita_lancamento,
            "ativo": c.ativo,
            "saldo": crud_plano_contas.calcular_saldo_conta(db, c.id)
        }
        for c in contas
    ]


@api_router.get("/contabilidade/plano-contas/{conta_id}")
def buscar_conta(conta_id: int, db: Session = Depends(get_db)):
    """Busca uma conta específica"""
    conta = crud_plano_contas.buscar_conta_por_id(db, conta_id)
    if not conta:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    
    return {
        "id": conta.id,
        "codigo": conta.codigo,
        "descricao": conta.descricao,
        "tipo": conta.tipo,
        "natureza": conta.natureza,
        "nivel": conta.nivel,
        "pai_id": conta.pai_id,
        "aceita_lancamento": conta.aceita_lancamento,
        "ativo": conta.ativo,
        "saldo": crud_plano_contas.calcular_saldo_conta(db, conta.id)
    }


@api_router.post("/contabilidade/plano-contas/inicializar")
def inicializar_plano_contas_endpoint(db: Session = Depends(get_db)):
    """Inicializa o plano de contas padrão"""
    from database.init_plano_contas import inicializar_plano_contas
    try:
        inicializar_plano_contas(db)
        return {"status": "ok", "message": "Plano de contas inicializado com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@api_router.get("/contabilidade/balanco-patrimonial")
def gerar_balanco_patrimonial(
    mes: int = Query(..., ge=1, le=12),
    ano: int = Query(..., ge=2000),
    db: Session = Depends(get_db)
):
    """Gera o Balanço Patrimonial para o período especificado"""
    balanco = crud_plano_contas.gerar_balanco_patrimonial(db, mes, ano)
    return balanco


# ===== SISTEMA DE PROVISÕES E PAGAMENTOS PARCIAIS =====

@api_router.get("/contabilidade/saldos-disponiveis/{mes}/{ano}", response_model=schemas.SaldosDisponiveisMes)
def obter_saldos_disponiveis(
    mes: int = Path(..., ge=1, le=12),
    ano: int = Path(..., ge=2000),
    db: Session = Depends(get_db)
):
    """
    Retorna saldos disponíveis do mês: provisões - pagamentos efetivos.
    Permite visualizar quanto ainda pode ser sacado de pró-labore, lucros, etc.
    """
    from database.crud_provisoes import get_saldo_disponivel_mes
    
    saldos = get_saldo_disponivel_mes(db, mes, ano)
    return saldos


@api_router.get("/contabilidade/provisoes-resumo/{mes}/{ano}")
def listar_provisoes_mes(
    mes: int = Path(..., ge=1, le=12),
    ano: int = Path(..., ge=2000),
    db: Session = Depends(get_db)
):
    """
    Lista todas as provisões do mês com detalhes das entradas.
    Útil para dashboard detalhado.
    """
    from database.crud_provisoes import listar_provisoes_mes as listar_prov
    
    provisoes = listar_prov(db, mes, ano)
    return {"mes": mes, "ano": ano, "provisoes": provisoes}


@api_router.post("/contabilidade/pagamento-pro-labore-parcial")
def registrar_pagamento_pro_labore(
    pagamento: schemas.PagamentoProLaboreCreate,
    db: Session = Depends(get_db)
):
    """
    Registra pagamento (parcial ou total) do pró‑labore do administrador como distribuição de lucros.
    
    Cria lançamentos (tipo 'pagamento_lucro'):
    - D: Lucros Distribuídos (3.4) / C: Caixa (1.1.1) - 89% (líquido)
    - D: Lucros Distribuídos (3.4) / C: INSS a Recolher (2.1.2.2) - 11% (retenção)
    """
    from database.crud_provisoes import get_saldo_disponivel_mes
    from database import models as _models
    
    # Validar saldo disponível
    saldos = get_saldo_disponivel_mes(db, pagamento.mes, pagamento.ano)
    
    if pagamento.valor > saldos['pro_labore']['disponivel']:
        raise HTTPException(
            status_code=400,
            detail=f"Valor solicitado (R$ {pagamento.valor:.2f}) excede saldo disponível (R$ {saldos['pro_labore']['disponivel']:.2f})"
        )
    
    # Buscar contas (migram para fluxo de lucros)
    conta_lucros_distribuidos = crud_plano_contas.buscar_conta_por_codigo(db, "3.4")
    conta_caixa = crud_plano_contas.buscar_conta_por_codigo(db, "1.1.1")
    conta_inss_passivo = crud_plano_contas.buscar_conta_por_codigo(db, "2.1.2.2")
    
    if not all([conta_lucros_distribuidos, conta_caixa, conta_inss_passivo]):
        raise HTTPException(status_code=500, detail="Contas contábeis não encontradas")
    
    mes_referencia = f"{pagamento.ano}-{str(pagamento.mes).zfill(2)}"
    
    # Calcular valores
    valor_liquido = pagamento.valor * 0.89  # 89% líquido
    valor_inss_retido = pagamento.valor * 0.11  # 11% INSS pessoal retido
    
    # Identificar sócio administrador (para registrar no histórico)
    socio_admin = db.query(_models.Socio).filter(_models.Socio.funcao.ilike('%admin%')).first()
    nome_admin = f" - {socio_admin.nome}" if socio_admin else ""

    historico_base = f"Pagamento pró-labore {pagamento.mes:02d}/{pagamento.ano}{nome_admin}"
    if pagamento.observacao:
        historico_base += f" - {pagamento.observacao}"
    
    # Lançamento 1: Pagamento líquido (D 3.4 / C 1.1.1)
    lanc1 = models.LancamentoContabil(
        data=pagamento.data_pagamento,
        conta_debito_id=conta_lucros_distribuidos.id,
        conta_credito_id=conta_caixa.id,
        valor=valor_liquido,
        historico=f"{historico_base} (líquido)",
        automatico=True,
        editavel=False,
        tipo_lancamento='pagamento_lucro',
        referencia_mes=mes_referencia
    )
    db.add(lanc1)
    
    # Lançamento 2: Retenção INSS 11% (D 3.4 / C 2.1.2.2)
    lanc2 = models.LancamentoContabil(
        data=pagamento.data_pagamento,
        conta_debito_id=conta_lucros_distribuidos.id,
        conta_credito_id=conta_inss_passivo.id,
        valor=valor_inss_retido,
        historico=f"{historico_base} (INSS 11% retido)",
        automatico=True,
        editavel=False,
        tipo_lancamento='pagamento_lucro',
        referencia_mes=mes_referencia
    )
    db.add(lanc2)
    
    db.commit()
    
    return {
        "status": "success",
        "message": f"Pagamento (como lucros) de R$ {pagamento.valor:.2f} registrado com sucesso",
        "valor_liquido": valor_liquido,
        "inss_retido": valor_inss_retido,
        "novo_saldo_disponivel": saldos['pro_labore']['disponivel'] - pagamento.valor
    }


@api_router.post("/contabilidade/pagamento-inss")
def registrar_pagamento_inss(
    pagamento: schemas.PagamentoINSSCreate,
    db: Session = Depends(get_db)
):
    """
    Registra pagamento de INSS (DARF).
    
    Cria lançamento:
    - D: INSS a Recolher (2.1.2.2) / C: Caixa (1.1.1)
    """
    from database.crud_provisoes import get_saldo_disponivel_mes
    
    # Validar saldo disponível
    saldos = get_saldo_disponivel_mes(db, pagamento.mes, pagamento.ano)
    
    if pagamento.valor > saldos['inss']['disponivel']:
        raise HTTPException(
            status_code=400,
            detail=f"Valor solicitado (R$ {pagamento.valor:.2f}) excede saldo disponível (R$ {saldos['inss']['disponivel']:.2f})"
        )
    
    # Buscar contas
    conta_inss_passivo = crud_plano_contas.buscar_conta_por_codigo(db, "2.1.2.2")
    conta_caixa = crud_plano_contas.buscar_conta_por_codigo(db, "1.1.1")
    
    if not all([conta_inss_passivo, conta_caixa]):
        raise HTTPException(status_code=500, detail="Contas contábeis não encontradas")
    
    mes_referencia = f"{pagamento.ano}-{str(pagamento.mes).zfill(2)}"
    
    historico = f"Pagamento DARF INSS {pagamento.mes:02d}/{pagamento.ano}"
    if pagamento.observacao:
        historico += f" - {pagamento.observacao}"
    
    lanc = models.LancamentoContabil(
        data=pagamento.data_pagamento,
        conta_debito_id=conta_inss_passivo.id,
        conta_credito_id=conta_caixa.id,
        valor=pagamento.valor,
        historico=historico,
        automatico=True,
        editavel=False,
        tipo_lancamento='pagamento_imposto',
        referencia_mes=mes_referencia
    )
    db.add(lanc)
    db.commit()
    
    return {
        "status": "success",
        "message": f"Pagamento de INSS R$ {pagamento.valor:.2f} registrado com sucesso",
        "novo_saldo_disponivel": saldos['inss']['disponivel'] - pagamento.valor
    }


@api_router.post("/contabilidade/pagamento-simples")
def registrar_pagamento_simples(
    pagamento: schemas.PagamentoSimplesCreate,
    db: Session = Depends(get_db)
):
    """
    Registra pagamento de Simples Nacional (DAS).
    
    Cria lançamento:
    - D: Simples a Recolher (2.1.2.1) / C: Caixa (1.1.1)
    """
    from database.crud_provisoes import get_saldo_disponivel_mes
    
    # Validar saldo disponível
    saldos = get_saldo_disponivel_mes(db, pagamento.mes, pagamento.ano)
    
    if pagamento.valor > saldos['simples']['disponivel']:
        raise HTTPException(
            status_code=400,
            detail=f"Valor solicitado (R$ {pagamento.valor:.2f}) excede saldo disponível (R$ {saldos['simples']['disponivel']:.2f})"
        )
    
    # Buscar contas
    conta_simples_passivo = crud_plano_contas.buscar_conta_por_codigo(db, "2.1.2.1")
    conta_caixa = crud_plano_contas.buscar_conta_por_codigo(db, "1.1.1")
    
    if not all([conta_simples_passivo, conta_caixa]):
        raise HTTPException(status_code=500, detail="Contas contábeis não encontradas")
    
    mes_referencia = f"{pagamento.ano}-{str(pagamento.mes).zfill(2)}"
    
    historico = f"Pagamento DAS Simples Nacional {pagamento.mes:02d}/{pagamento.ano}"
    if pagamento.observacao:
        historico += f" - {pagamento.observacao}"
    
    lanc = models.LancamentoContabil(
        data=pagamento.data_pagamento,
        conta_debito_id=conta_simples_passivo.id,
        conta_credito_id=conta_caixa.id,
        valor=pagamento.valor,
        historico=historico,
        automatico=True,
        editavel=False,
        tipo_lancamento='pagamento_imposto',
        referencia_mes=mes_referencia
    )
    db.add(lanc)
    db.commit()
    
    return {
        "status": "success",
        "message": f"Pagamento de Simples R$ {pagamento.valor:.2f} registrado com sucesso",
        "novo_saldo_disponivel": saldos['simples']['disponivel'] - pagamento.valor
    }


@api_router.post("/contabilidade/pagamento-lucro-socio")
def registrar_pagamento_lucro_socio(
    pagamento: schemas.PagamentoLucroSocioCreate,
    db: Session = Depends(get_db)
):
    """
    Registra saque de lucro de um sócio.
    
    Cria lançamento:
    - D: Lucros Distribuídos (3.4) / C: Caixa (1.1.1)
    """
    from database.crud_provisoes import get_saldo_disponivel_mes
    
    # Validar saldo disponível
    saldos = get_saldo_disponivel_mes(db, pagamento.mes, pagamento.ano)
    
    # Buscar saldo do sócio específico
    lucro_socio = next(
        (s for s in saldos['lucros_por_socio'] if s['socio_id'] == pagamento.socio_id),
        None
    )
    
    if not lucro_socio:
        raise HTTPException(status_code=404, detail="Sócio não encontrado ou sem lucros neste mês")
    
    if pagamento.valor > lucro_socio['disponivel']:
        raise HTTPException(
            status_code=400,
            detail=f"Valor solicitado (R$ {pagamento.valor:.2f}) excede saldo disponível (R$ {lucro_socio['disponivel']:.2f})"
        )
    
    # Buscar sócio
    socio = db.query(models.Socio).filter(models.Socio.id == pagamento.socio_id).first()
    if not socio:
        raise HTTPException(status_code=404, detail="Sócio não encontrado")
    
    # Buscar contas
    conta_lucros_distribuidos = crud_plano_contas.buscar_conta_por_codigo(db, "3.4")
    conta_caixa = crud_plano_contas.buscar_conta_por_codigo(db, "1.1.1")
    
    if not all([conta_lucros_distribuidos, conta_caixa]):
        raise HTTPException(status_code=500, detail="Contas contábeis não encontradas")
    
    mes_referencia = f"{pagamento.ano}-{str(pagamento.mes).zfill(2)}"
    
    historico = f"Saque de lucro - {socio.nome} - {pagamento.mes:02d}/{pagamento.ano}"
    if pagamento.observacao:
        historico += f" - {pagamento.observacao}"
    
    lanc = models.LancamentoContabil(
        data=pagamento.data_pagamento,
        conta_debito_id=conta_lucros_distribuidos.id,
        conta_credito_id=conta_caixa.id,
        valor=pagamento.valor,
        historico=historico,
        automatico=True,
        editavel=False,
        tipo_lancamento='pagamento_lucro',
        referencia_mes=mes_referencia
    )
    db.add(lanc)
    db.commit()
    
    return {
        "status": "success",
        "message": f"Saque de lucro de R$ {pagamento.valor:.2f} para {socio.nome} registrado com sucesso",
        "novo_saldo_disponivel": lucro_socio['disponivel'] - pagamento.valor
    }


# ===== LANÇAMENTOS CONTÁBEIS =====

@api_router.get("/contabilidade/lancamentos")
def listar_lancamentos(
    data_inicio: Optional[date_type] = None,
    data_fim: Optional[date_type] = None,
    conta_id: Optional[int] = None,
    tipo_lancamento: Optional[str] = None,
    apenas_pendentes: bool = False,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Lista lançamentos contábeis com filtros.
    
    Novos filtros:
    - tipo_lancamento: 'efetivo', 'provisao', 'pagamento_pro_labore', 'pagamento_lucro', 'pagamento_imposto'
    - apenas_pendentes: True = apenas provisões não pagas
    """
    lancamentos = crud_plano_contas.listar_lancamentos(
        db, data_inicio, data_fim, conta_id, tipo_lancamento, apenas_pendentes, limit, offset
    )
    return [
        {
            "id": l.id,
            "data": l.data.isoformat(),
            "debito_conta_id": l.conta_debito.id,
            "debito_conta_codigo": l.conta_debito.codigo,
            "debito_conta_nome": l.conta_debito.descricao,
            "credito_conta_id": l.conta_credito.id,
            "credito_conta_codigo": l.conta_credito.codigo,
            "credito_conta_nome": l.conta_credito.descricao,
            "valor": l.valor,
            "historico": l.historico,
            "automatico": l.automatico,
            "editavel": l.editavel,
            "criado_em": l.criado_em.isoformat() if l.criado_em else None,
            "editado_em": l.editado_em.isoformat() if l.editado_em else None,
            "entrada_id": l.entrada_id,
            "despesa_id": l.despesa_id,
            # Campos de provisão
            "tipo_lancamento": l.tipo_lancamento,
            "referencia_mes": l.referencia_mes,
            "pago": l.pago,
            "data_pagamento": l.data_pagamento.isoformat() if l.data_pagamento else None,
            "valor_pago": l.valor_pago,
            "saldo_pendente": l.valor - (l.valor_pago or 0) if not l.pago else 0
        }
        for l in lancamentos
    ]


@api_router.post("/contabilidade/lancamentos/{lancamento_id}/marcar-pagamento")
def marcar_pagamento(
    lancamento_id: int,
    data_pagamento: date_type = Body(...),
    valor_pago: Optional[float] = Body(None),
    observacao: Optional[str] = Body(None),
    db: Session = Depends(get_db)
):
    """
    Marca um lançamento de provisão como pago (total ou parcial).
    
    Se valor_pago < valor provisionado:
    - Marca lançamento como pago
    - Cria lançamento(s) de pagamento efetivo
    - Cria novo lançamento de provisão com saldo restante
    
    Body:
    - data_pagamento: Data do pagamento efetivo
    - valor_pago: Valor pago (se None, paga total). Pode ser parcial
    - observacao: Observação para histórico
    """
    try:
        resultado = crud_plano_contas.marcar_pagamento_lancamento(
            db=db,
            lancamento_id=lancamento_id,
            data_pagamento=data_pagamento,
            valor_pago=valor_pago,
            observacao=observacao
        )
        return {
            "status": "success",
            "message": "Pagamento registrado com sucesso",
            **resultado
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao registrar pagamento: {str(e)}")


@api_router.post("/contabilidade/lancamentos")
def criar_lancamento_manual(
    data: date_type = Body(...),
    debito_conta_id: int = Body(...),
    credito_conta_id: int = Body(...),
    valor: float = Body(...),
    historico: str = Body(...),
    db: Session = Depends(get_db)
):
    """Cria um lançamento contábil manual"""
    try:
        lancamento = crud_plano_contas.criar_lancamento(
            db=db,
            data=data,
            conta_debito_id=debito_conta_id,
            conta_credito_id=credito_conta_id,
            valor=valor,
            historico=historico,
            automatico=False,
            editavel=True
        )
        return {
            "id": lancamento.id,
            "data": lancamento.data.isoformat(),
            "valor": lancamento.valor,
            "historico": lancamento.historico,
            "status": "ok"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@api_router.put("/contabilidade/lancamentos/{lancamento_id}")
def editar_lancamento_endpoint(
    lancamento_id: int,
    data: date_type = Body(...),
    debito_conta_id: int = Body(...),
    credito_conta_id: int = Body(...),
    valor: float = Body(...),
    historico: str = Body(...),
    db: Session = Depends(get_db)
):
    """Edita um lançamento contábil"""
    try:
        lancamento = crud_plano_contas.editar_lancamento(
            db, lancamento_id, data, debito_conta_id, credito_conta_id, valor, historico
        )
        return {"id": lancamento.id, "status": "ok", "message": "Lançamento editado com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@api_router.delete("/contabilidade/lancamentos/{lancamento_id}")
def excluir_lancamento_endpoint(lancamento_id: int, db: Session = Depends(get_db)):
    """Exclui um lançamento contábil"""
    try:
        crud_plano_contas.excluir_lancamento(db, lancamento_id)
        return {"status": "ok", "message": "Lançamento excluído com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


def _calcular_dre_mes(db: Session, year: int, month: int):
    """
    Função auxiliar para calcular DRE de um mês específico em tempo real.
    Retorna um dicionário com os valores calculados ou None se não houver movimentação.
    """
    from utils.datas import inicio_do_mes, fim_do_mes, ultimos_12_meses
    from utils.simples import calcular_faixa_simples, calcular_imposto_simples
    from sqlalchemy import func
    
    mes_str = f"{year}-{str(month).zfill(2)}"
    inicio = inicio_do_mes(mes_str)
    fim = fim_do_mes(mes_str)
    
    # Calcular receita bruta do mês
    receita_bruta = db.query(func.sum(models.Entrada.valor)).filter(
        models.Entrada.data >= inicio,
        models.Entrada.data <= fim
    ).scalar() or 0.0
    
    # Se não há receita, não calcular DRE
    if receita_bruta == 0:
        return None
    
    # Calcular receita acumulada 12 meses
    meses_12 = ultimos_12_meses(mes_str)
    receita_12m = 0.0
    for mes_ant in meses_12:
        inicio_ant = inicio_do_mes(mes_ant)
        fim_ant = fim_do_mes(mes_ant)
        receita_mes_ant = db.query(func.sum(models.Entrada.valor)).filter(
            models.Entrada.data >= inicio_ant,
            models.Entrada.data <= fim_ant
        ).scalar() or 0.0
        receita_12m += receita_mes_ant
    
    # Calcular faixa Simples e alíquotas
    try:
        aliquota, deducao, aliquota_efetiva = calcular_faixa_simples(receita_12m, inicio, db)
    except (ValueError, Exception):
        aliquota = 0.045  # 4.5% primeira faixa como padrão
        deducao = 0.0
        aliquota_efetiva = 0.0
    
    # Calcular imposto do mês
    imposto = calcular_imposto_simples(receita_bruta, aliquota_efetiva)
    
    # Calcular despesas gerais do mês
    despesas_gerais = db.query(func.sum(models.Despesa.valor)).filter(
        models.Despesa.data >= inicio,
        models.Despesa.data <= fim
    ).scalar() or 0.0
    
    # Cálculo revertido para manter consistência com DRE consolidada
    # Pró-labore e INSS não entram no cálculo (zerados)
    pro_labore = 0.0
    inss_patronal = 0.0
    inss_pessoal = 0.0
    lucro_liquido = receita_bruta - imposto - despesas_gerais
    
    return {
        "receita_bruta": float(receita_bruta),
        "receita_12m": float(receita_12m),
        "aliquota": float(aliquota),
        "aliquota_efetiva": float(aliquota_efetiva),
        "deducao": float(deducao),
        "imposto": float(imposto),
        "pro_labore": float(pro_labore),
        "inss_patronal": float(inss_patronal),
        "inss_pessoal": float(inss_pessoal),
        "despesas_gerais": float(despesas_gerais),
        "lucro_liquido": float(lucro_liquido),
        "reserva_10p": float(lucro_liquido * 0.10)
    }


@api_router.get("/contabilidade/pro-labore/{socio_id}")
def calcular_pro_labore_socio(
    socio_id: int,
    year: int = Query(...),
    db: Session = Depends(get_db)
):
    """
    Calcula o pró-labore mensal de um sócio baseado nas suas contribuições reais
    registradas na tabela EntradaSocio (percentual por entrada).
    
    Fórmula:
    1. Faturamento total do mês = soma de todas as entradas
    2. Contribuição do sócio = soma(entrada.valor * entrada_socio.percentual / 100)
    3. Percentual de contribuição = contribuição_socio / faturamento_total * 100
    4. Lucro disponível total = lucro_liquido * 85% (descontando 5% pró-labore + 10% fundo)
    5. Lucro disponível do sócio = lucro_disponivel_total * (percentual_contribuicao / 100)
    6. Lucro final = lucro_disponivel_socio - pro_labore_liquido - inss_patronal
    
    IMPORTANTE: Calcula DRE automaticamente em tempo real se não existir consolidado.
    """
    # Verificar se o sócio existe
    socio = db.query(models.Socio).filter(models.Socio.id == socio_id).first()
    if not socio:
        raise HTTPException(status_code=404, detail="Sócio não encontrado")
    
    resultado = []
    
    for month in range(1, 13):
        # Buscar DRE do mês (formato: "YYYY-MM")
        mes_str = f"{year}-{str(month).zfill(2)}"
        dre = db.query(models.DREMensal).filter(
            models.DREMensal.mes == mes_str
        ).first()
        
        # Se não tiver DRE ou não estiver consolidado, calcular em tempo real
        lucro_liquido = 0
        if dre and dre.consolidado:
            # Usar DRE consolidado
            lucro_liquido = float(dre.lucro_liquido or 0)
        else:
            # Calcular DRE em tempo real
            dre_calculado = _calcular_dre_mes(db, year, month)
            if dre_calculado:
                lucro_liquido = dre_calculado["lucro_liquido"]
            else:
                # Sem movimentação no mês, pular
                continue
        
        # Calcular faturamento total do mês
        entradas_mes = db.query(models.Entrada).filter(
            extract('year', models.Entrada.data) == year,
            extract('month', models.Entrada.data) == month
        ).all()
        
        faturamento_total = sum(float(entrada.valor or 0) for entrada in entradas_mes)
        
        if faturamento_total == 0:
            # Sem faturamento, não há contribuição
            resultado.append({
                "mes": month,
                "ano": year,
                "faturamento_total": 0,
                "contribuicao_socio": 0,
                "percentual_contribuicao": 0,
                "lucro_liquido": lucro_liquido,
                "pro_labore_bruto": 0,
                "fundo_reserva": 0,
                "lucro_disponivel_total": 0,
                "lucro_disponivel_socio": 0,
                "pro_labore_liquido": 0,
                "inss_patronal": 0,
                "lucro_final_socio": 0
            })
            continue
        
        # Calcular contribuição do sócio (soma de entrada.valor * percentual)
        contribuicao_socio = 0
        for entrada in entradas_mes:
            # Buscar o percentual do sócio nesta entrada
            entrada_socio = db.query(models.EntradaSocio).filter(
                models.EntradaSocio.entrada_id == entrada.id,
                models.EntradaSocio.socio_id == socio_id
            ).first()
            
            if entrada_socio:
                # Percentual já está no formato correto (50 = 50%, 1 = 1%, 0.5 = 0.5%)
                percentual = float(entrada_socio.percentual or 0)
                contribuicao_socio += float(entrada.valor or 0) * (percentual / 100)
        
        # Percentual de contribuição do sócio no mês (já em formato percentual 0-100)
        percentual_contribuicao = (contribuicao_socio / faturamento_total * 100) if faturamento_total > 0 else 0
        
        # Verificar se este sócio é o administrador
        is_admin = socio and 'administrador' in (socio.funcao or '').lower()
        
        # Calcular fundo de reserva (10% do lucro líquido)
        fundo_reserva = lucro_liquido * 0.10
        lucro_disponivel_total = lucro_liquido * 0.85  # 85% disponível
        
        # Inicializar variáveis
        pro_labore_bruto_total = 0.0
        inss_patronal_total = 0.0
        inss_pessoal_total = 0.0
        pro_labore_liquido = 0.0
        lucro_final_socio = 0.0
        
        if is_admin:
            # Para o administrador, pegar o pró-labore calculado na DRE
            if dre and dre.consolidado:
                pro_labore_bruto_total = float(dre.pro_labore or 0)
                inss_patronal_total = float(dre.inss_patronal or 0)
                inss_pessoal_total = float(dre.inss_pessoal or 0)
            elif dre_calculado:
                pro_labore_bruto_total = dre_calculado.get("pro_labore", 0)
                inss_patronal_total = dre_calculado.get("inss_patronal", 0)
                inss_pessoal_total = dre_calculado.get("inss_pessoal", 0)
            
            # Pró-labore líquido = bruto - INSS pessoal
            pro_labore_liquido = pro_labore_bruto_total - inss_pessoal_total
            # O lucro do administrador É o pró-labore líquido
            lucro_final_socio = pro_labore_liquido
        else:
            # Para sócios não-administradores, distribuir o lucro disponível
            lucro_final_socio = lucro_disponivel_total * (percentual_contribuicao / 100)
        
        resultado.append({
            "mes": month,
            "ano": year,
            "faturamento_total": round(faturamento_total, 2),
            "contribuicao_socio": round(contribuicao_socio, 2),
            "percentual_contribuicao": round(percentual_contribuicao, 2),
            "lucro_liquido": round(lucro_liquido, 2),
            "pro_labore_bruto": round(pro_labore_bruto_total, 2),
            "inss_pessoal": round(inss_pessoal_total, 2),
            "inss_patronal": round(inss_patronal_total, 2),
            "pro_labore_liquido": round(pro_labore_liquido, 2),
            "fundo_reserva": round(fundo_reserva, 2),
            "lucro_disponivel_total": round(lucro_disponivel_total, 2),
            "lucro_final_socio": round(lucro_final_socio, 2)
        })
    
    return {
        "socio_id": socio_id,
        "socio_nome": socio.nome,
        "ano": year,
        "meses": resultado
    }


# Processos endpoints
@api_router.get("/processos", response_model=list[schemas.Processo])
def listar_processos(db: Session = Depends(get_db)):
    start_time = time.time()  # Start timing
    processos = db.query(models.Processo).options(
        joinedload(models.Processo.cliente),
        joinedload(models.Processo.municipio)
    ).all()
    end_time = time.time()  # End timing
    print(f"Query execution time: {end_time - start_time} seconds")  # Log the time
    return processos


@api_router.get("/processos/{processo_id}", response_model=schemas.Processo)
def get_processo(processo_id: int, db: Session = Depends(get_db)):
    p = crud_processos.buscar_processo(db, processo_id)
    if not p:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    return p


@api_router.post("/processos", response_model=schemas.Processo)
def criar_processo(processo: schemas.ProcessoCreate, db: Session = Depends(get_db)):
    p = crud_processos.criar_processo(
        processo.numero,
        processo.autor,
        processo.reu,
        processo.fase,
        processo.uf,
        processo.comarca,
        processo.vara,
        processo.status,
        processo.observacoes,
        processo.data_abertura,
        processo.data_fechamento,
        processo.cliente_id,
        db,
    )
    return p


@api_router.put("/processos/{processo_id}", response_model=schemas.Processo)
def atualizar_processo_api(processo_id: int, processo: schemas.ProcessoUpdate, db: Session = Depends(get_db)):
    p = crud_processos.atualizar_processo(db, processo_id, processo.model_dump(exclude_unset=True))
    if not p:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    return p


@api_router.delete("/processos/{processo_id}")
def deletar_processo_api(processo_id: int, db: Session = Depends(get_db)):
    crud_processos.deletar_processo(processo_id, db)
    return {"status": "ok"}


# Tarefas endpoints
@api_router.get("/tarefas", response_model=list[schemas.Tarefa])
def listar_tarefas(db: Session = Depends(get_db)):
    return crud_tarefas.listar_tarefas_gerais(db)


@api_router.get("/tarefas/{tarefa_id}", response_model=schemas.Tarefa)
def get_tarefa(tarefa_id: int, db: Session = Depends(get_db)):
    t = crud_tarefas.buscar_tarefa(tarefa_id, db)
    if not t:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    return t


@api_router.post("/tarefas", response_model=schemas.Tarefa)
def criar_tarefa_api(t: schemas.TarefaCreate, db: Session = Depends(get_db)):
    n = crud_tarefas.criar_tarefa(t.titulo, t.descricao, t.prazo, t.responsavel_id, t.processo_id, t.status, db)
    return n


@api_router.put("/tarefas/{tarefa_id}", response_model=schemas.Tarefa)
def atualizar_tarefa_api(tarefa_id: int, t: schemas.TarefaUpdate, db: Session = Depends(get_db)):
    updated = crud_tarefas.atualizar_tarefa(tarefa_id, db, **t.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    return updated


@api_router.delete("/tarefas/{tarefa_id}")
def deletar_tarefa_api(tarefa_id: int, db: Session = Depends(get_db)):
    crud_tarefas.deletar_tarefa(tarefa_id, db)
    return {"status": "ok"}


# Andamentos endpoints
@api_router.get("/andamentos/{processo_id}", response_model=list[schemas.Andamento])
def listar_andamentos_do_processo(processo_id: int, db: Session = Depends(get_db)):
    return crud_andamentos.listar_andamentos_do_processo(processo_id, db)


@api_router.post("/andamentos", response_model=schemas.Andamento)
def criar_andamento_api(a: schemas.AndamentoCreate, db: Session = Depends(get_db)):
    na = crud_andamentos.criar_andamento(a.processo_id, a.descricao, a.tipo, a.criado_por, a.data, db)
    return na


@api_router.delete("/andamentos/{andamento_id}")
def deletar_andamento_api(andamento_id: int, db: Session = Depends(get_db)):
    crud_andamentos.deletar_andamento(andamento_id, db)
    return {"status": "ok"}


# Anexos endpoints
@api_router.get("/anexos/processo/{processo_id}", response_model=list[schemas.Anexo])
def listar_anexos_processo(processo_id: int, db: Session = Depends(get_db)):
    return crud_anexos.listar_anexos_do_processo(processo_id, db)


@api_router.post("/anexos", response_model=schemas.Anexo)
def criar_anexo_api(a: schemas.AnexoCreate, db: Session = Depends(get_db)):
    na = crud_anexos.criar_anexo(a.processo_id, a.andamento_id, a.nome_original, a.caminho_arquivo, a.mime, a.tamanho, a.criado_por, db)
    return na


@api_router.delete("/anexos/{anexo_id}")
def deletar_anexo_api(anexo_id: int, db: Session = Depends(get_db)):
    crud_anexos.deletar_anexo(anexo_id, db)
    return {"status": "ok"}


# Pagamentos endpoints
@api_router.get("/pagamentos", response_model=list[schemas.Pagamento])
def listar_pagamentos(db: Session = Depends(get_db)):
    return crud_pagamentos.listar_pagamentos(db)


@api_router.post("/pagamentos", response_model=schemas.Pagamento)
def criar_pagamento_api(p: schemas.PagamentoCreate, db: Session = Depends(get_db)):
    return crud_pagamentos.criar_pagamento(p.descricao, p.valor, p.tipo, p.processo_id, p.data_pagamento, db)


@api_router.delete("/pagamentos/{pagamento_id}")
def deletar_pagamento_api(pagamento_id: int, db: Session = Depends(get_db)):
    crud_pagamentos.deletar_pagamento(pagamento_id, db)
    return {"status": "ok"}


# Usuarios endpoints
@api_router.get("/usuarios", response_model=list[schemas.Usuario])
def listar_usuarios(db: Session = Depends(get_db)):
    return crud_usuarios.listar_usuarios(db)


@api_router.post("/usuarios", response_model=schemas.Usuario)
def criar_usuario_api(u: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    return crud_usuarios.criar_usuario(db, **u.model_dump())

@api_router.put("/usuarios/{usuario_id}", response_model=schemas.Usuario)
def atualizar_usuario_api(usuario_id: int, usuario: schemas.UsuarioUpdate, db: Session = Depends(get_db)):
    u = crud_usuarios.atualizar_usuario(usuario_id, db, **usuario.model_dump(exclude_unset=True))
    if not u:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return u

@api_router.delete("/usuarios/{usuario_id}")
def deletar_usuario_api(usuario_id: int, db: Session = Depends(get_db)):
    crud_usuarios.deletar_usuario(usuario_id, db)
    return {"status": "ok"}


# ==================== MUNICÍPIOS ENDPOINTS ====================

@api_router.get("/municipios", response_model=List[schemas.MunicipioResponse])
def listar_municipios(db: Session = Depends(get_db)):
    """Lista todos os municípios cadastrados."""
    return crud_municipios.listar_municipios(db)


@api_router.get("/municipios/uf/{uf}", response_model=List[schemas.MunicipioResponse])
def listar_municipios_por_uf(uf: str, db: Session = Depends(get_db)):
    """Lista municípios de uma UF específica."""
    municipios = crud_municipios.listar_municipios_por_uf(uf, db)
    if not municipios:
        raise HTTPException(status_code=404, detail=f"Nenhum município encontrado para UF: {uf}")
    return municipios


@api_router.get("/municipios/{municipio_id}", response_model=schemas.MunicipioResponse)
def buscar_municipio(municipio_id: int, db: Session = Depends(get_db)):
    """Busca um município por ID."""
    municipio = crud_municipios.buscar_municipio_por_id(municipio_id, db)
    if not municipio:
        raise HTTPException(status_code=404, detail="Município não encontrado")
    return municipio


# ==================== FERIADOS ENDPOINTS ====================

@api_router.get("/feriados", response_model=List[schemas.FeriadoResponse])
def listar_feriados(
    tipo: Optional[str] = None,
    uf: Optional[str] = None,
    municipio_id: Optional[int] = None,
    ano: Optional[int] = None,
    data_inicio: Optional[date_type] = None,
    data_fim: Optional[date_type] = None,
    db: Session = Depends(get_db)
):
    """
    Lista feriados com filtros opcionais.
    Query params: tipo, uf, municipio_id, ano, data_inicio, data_fim
    """
    return crud_feriados.listar_feriados(
        db, tipo=tipo, uf=uf, municipio_id=municipio_id,
        ano=ano, data_inicio=data_inicio, data_fim=data_fim
    )


@api_router.get("/feriados/{feriado_id}", response_model=schemas.FeriadoResponse)
def buscar_feriado(feriado_id: int, db: Session = Depends(get_db)):
    """Busca um feriado por ID."""
    feriado = crud_feriados.buscar_feriado_por_id(feriado_id, db)
    if not feriado:
        raise HTTPException(status_code=404, detail="Feriado não encontrado")
    return feriado


@api_router.post("/feriados", response_model=schemas.FeriadoResponse)
def criar_feriado(feriado: schemas.FeriadoCreate, db: Session = Depends(get_db)):
    """Cria um novo feriado."""
    try:
        return crud_feriados.criar_feriado(
            db=db,
            data=feriado.data,
            nome=feriado.nome,
            tipo=feriado.tipo.value,
            uf=feriado.uf,
            municipio_id=feriado.municipio_id,
            recorrente=feriado.recorrente,
            criado_por=None  # TODO: pegar do usuário logado
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@api_router.put("/feriados/{feriado_id}", response_model=schemas.FeriadoResponse)
def atualizar_feriado(feriado_id: int, feriado: schemas.FeriadoUpdate, db: Session = Depends(get_db)):
    """Atualiza um feriado existente."""
    try:
        updated = crud_feriados.atualizar_feriado(
            feriado_id, db, **feriado.model_dump(exclude_unset=True)
        )
        if not updated:
            raise HTTPException(status_code=404, detail="Feriado não encontrado")
        return updated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@api_router.delete("/feriados/{feriado_id}")
def deletar_feriado(feriado_id: int, db: Session = Depends(get_db)):
    """Deleta um feriado."""
    sucesso = crud_feriados.deletar_feriado(feriado_id, db)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Feriado não encontrado")
    return {"status": "ok"}


@api_router.get("/feriados/calendario/{ano}/{mes}/{municipio_id}", response_model=List[schemas.CalendarioDiaResponse])
def obter_calendario_mes(
    ano: int,
    mes: int,
    municipio_id: int = None,
    db: Session = Depends(get_db)
):
    """
    Retorna informações de cada dia do mês para renderizar calendário.
    Indica dias úteis, feriados e fins de semana.
    """
    if mes < 1 or mes > 12:
        raise HTTPException(status_code=400, detail="Mês deve estar entre 1 e 12")
    
    return crud_feriados.obter_calendario_mes(ano, mes, municipio_id, db)


# ==================== TIPOS DE TAREFA E ANDAMENTO ====================

@api_router.get("/tipos-tarefa", response_model=List[schemas.TipoTarefaResponse])
def listar_tipos_tarefa(db: Session = Depends(get_db)):
    """Lista todos os tipos de tarefa disponíveis."""
    from database.models import TipoTarefa
    tipos = db.query(TipoTarefa).all()
    return tipos


@api_router.get("/tipos-andamento", response_model=List[schemas.TipoAndamentoResponse])
def listar_tipos_andamento(db: Session = Depends(get_db)):
    """Lista todos os tipos de andamento disponíveis."""
    from database.models import TipoAndamento
    tipos = db.query(TipoAndamento).all()
    return tipos


# ==================== TAREFAS COM WORKFLOW ENDPOINTS ====================

@api_router.post("/processos/{processo_id}/tarefas", response_model=schemas.TarefaResponse)
def criar_tarefa_processo(
    processo_id: int,
    tarefa: schemas.TarefaCreate,
    db: Session = Depends(get_db)
):
    """Cria uma nova tarefa manualmente para um processo."""
    # Valida se processo existe
    processo = crud_processos.buscar_processo(db, processo_id)
    if not processo:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    
    # Cria tarefa
    nova_tarefa = crud_tarefas.criar_tarefa(
        db=db,
        processo_id=processo_id,
        tipo_tarefa_id=tarefa.tipo_tarefa_id,
        descricao_complementar=tarefa.descricao_complementar,
        prazo=tarefa.prazo_fatal,
        responsavel_id=tarefa.responsavel_id,
        status=tarefa.status
    )
    
    # Atualiza prazos se fornecidos
    if tarefa.prazo_administrativo or tarefa.prazo_fatal:
        crud_tarefas.atualizar_tarefa(
            nova_tarefa.id,
            db,
            prazo_administrativo=tarefa.prazo_administrativo,
            prazo_fatal=tarefa.prazo_fatal
        )
    
    db.refresh(nova_tarefa)
    return nova_tarefa


@api_router.post("/processos/{processo_id}/tarefas/intimacao", response_model=schemas.TarefaResponse)
def criar_tarefa_intimacao(
    processo_id: int,
    tarefa: schemas.TarefaIntimacaoCreate,
    db: Session = Depends(get_db)
):
    """
    Cria tarefa de análise de intimação com cálculo automático de prazos.
    Prazo administrativo: +2 dias úteis
    Prazo fatal: +3 dias úteis
    """
    # Valida processo
    processo = crud_processos.buscar_processo(db, processo_id)
    if not processo:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    
    # Busca tipo de tarefa "Análise de Intimação"
    from database.models import TipoTarefa
    tipo = db.query(TipoTarefa).filter(TipoTarefa.nome == "Análise de Intimação").first()
    if not tipo:
        raise HTTPException(status_code=400, detail="Tipo 'Análise de Intimação' não encontrado")
    
    # Calcula prazos
    hoje = date_type.today()
    municipio_id = processo.municipio_id if processo.municipio_id else None
    
    prazo_admin = prazos.adicionar_dias_uteis(hoje, 2, municipio_id, db)
    prazo_fatal_calc = prazos.adicionar_dias_uteis(hoje, 3, municipio_id, db)
    
    # Gera nome contextual baseado na fase
    fase = processo.fase or "Inicial"
    descricao = f"Análise de Intimação {fase}"
    
    # Cria tarefa
    nova_tarefa = models.Tarefa(
        processo_id=processo_id,
        tipo_tarefa_id=tipo.id,
        descricao_complementar=descricao,
        conteudo_intimacao=tarefa.conteudo_intimacao,
        responsavel_id=tarefa.responsavel_id,
        prazo_administrativo=prazo_admin,
        prazo_fatal=prazo_fatal_calc,
        prazo=prazo_fatal_calc,
        etapa_workflow_atual="analise_pendente",
        status="pendente"
    )
    
    db.add(nova_tarefa)
    db.commit()
    db.refresh(nova_tarefa)
    return nova_tarefa


@api_router.patch("/tarefas/{tarefa_id}/classificar", response_model=schemas.TarefaResponse)
def classificar_intimacao(
    tarefa_id: int,
    classificacao: schemas.TarefaIntimacaoClassificar,
    usuario_id: int = 1,  # TODO: pegar do token de autenticação
    db: Session = Depends(get_db)
):
    """
    Classifica uma intimação e cria andamento/tarefa derivada conforme necessário.
    """
    # Busca tarefa
    tarefa = crud_tarefas.buscar_tarefa(tarefa_id, db)
    if not tarefa:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    
    # Valida permissão (apenas responsável pode classificar)
    if tarefa.responsavel_id != usuario_id:
        raise HTTPException(status_code=403, detail="Apenas o responsável pode classificar esta intimação")
    
    # Atualiza classificação e conteúdo
    tarefa.classificacao_intimacao = classificacao.classificacao_intimacao.value
    if classificacao.conteudo_decisao:
        tarefa.conteudo_decisao = classificacao.conteudo_decisao
    
    # Cria andamento apenas para "Decisão Interlocutória" e "Sentença"
    if classificacao.classificacao_intimacao in [
        schemas.ClassificacaoIntimacao.DECISAO_INTERLOCUTORIA,
        schemas.ClassificacaoIntimacao.SENTENCA
    ]:
        from database.models import TipoAndamento
        tipo_andamento = db.query(TipoAndamento).filter(
            TipoAndamento.nome == classificacao.classificacao_intimacao.value
        ).first()
        
        if tipo_andamento:
            novo_andamento = models.Andamento(
                processo_id=tarefa.processo_id,
                tipo_andamento_id=tipo_andamento.id,
                descricao_complementar=classificacao.conteudo_decisao,
                data=date_type.today(),
                criado_por=usuario_id
            )
            db.add(novo_andamento)
    
    # Cria tarefa derivada se solicitado
    if classificacao.criar_tarefa_derivada and classificacao.tipo_tarefa_derivada_id:
        if not classificacao.responsavel_derivado_id:
            raise HTTPException(status_code=400, detail="Responsável da tarefa derivada é obrigatório")
        
        # Para Petição e Recurso, prazo fatal é obrigatório
        from database.models import TipoTarefa
        tipo_derivado = db.query(TipoTarefa).filter(TipoTarefa.id == classificacao.tipo_tarefa_derivada_id).first()
        
        prazo_admin_derivado = None
        prazo_fatal_derivado = None
        
        if tipo_derivado and tipo_derivado.nome in ["Petição", "Recurso"]:
            if not classificacao.prazo_fatal_derivada:
                raise HTTPException(
                    status_code=400,
                    detail=f"Prazo fatal é obrigatório para tarefa do tipo '{tipo_derivado.nome}'"
                )
            # Calcula prazo administrativo: 2 dias úteis antes do prazo fatal
            prazo_fatal_derivado = classificacao.prazo_fatal_derivada
            municipio_id = tarefa.processo.municipio_id if tarefa.processo else None
            prazo_admin_derivado = prazos.subtrair_dias_uteis(prazo_fatal_derivado, 2, municipio_id, db)
        else:
            prazo_fatal_derivado = classificacao.prazo_fatal_derivada
            if prazo_fatal_derivado:
                municipio_id = tarefa.processo.municipio_id if tarefa.processo else None
                prazo_admin_derivado = prazos.subtrair_dias_uteis(prazo_fatal_derivado, 2, municipio_id, db)
        
        # Cria tarefa derivada
        crud_tarefas.criar_tarefa_derivada(
            tarefa_origem_id=tarefa_id,
            tipo_tarefa_id=classificacao.tipo_tarefa_derivada_id,
            processo_id=tarefa.processo_id,
            responsavel_id=classificacao.responsavel_derivado_id,
            prazo_administrativo=prazo_admin_derivado,
            prazo_fatal=prazo_fatal_derivado,
            descricao_complementar=f"Derivada de: {tarefa.tipo_tarefa.nome if tarefa.tipo_tarefa else 'Tarefa'}",
            db=db
        )
    
    # Avança workflow para "intimacao_classificada"
    tarefa.etapa_workflow_atual = "intimacao_classificada"
    
    # Adiciona ao histórico
    historico = tarefa.workflow_historico or []
    historico.append({
        "etapa_anterior": "analise_pendente",
        "etapa_nova": "intimacao_classificada",
        "usuario_id": usuario_id,
        "usuario_nome": "Usuário",  # TODO: buscar nome real
        "timestamp": datetime.utcnow().isoformat(),
        "acao": f"Intimação classificada como: {classificacao.classificacao_intimacao.value}"
    })
    tarefa.workflow_historico = historico
    
    db.commit()
    db.refresh(tarefa)
    return tarefa


@api_router.patch("/tarefas/{tarefa_id}/workflow/avancar", response_model=schemas.TarefaResponse)
def avancar_workflow(
    tarefa_id: int,
    avancar: schemas.TarefaWorkflowAvancar,
    usuario_id: int = 1,  # TODO: pegar do token
    db: Session = Depends(get_db)
):
    """Avança o workflow de uma tarefa para próxima etapa."""
    tarefa = crud_tarefas.buscar_tarefa(tarefa_id, db)
    if not tarefa:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    
    # Busca nome do usuário
    usuario = crud_usuarios.buscar_usuario(db, usuario_id)
    usuario_nome = usuario.nome if usuario else "Desconhecido"
    
    try:
        tarefa_atualizada = crud_tarefas.avancar_workflow_tarefa(
            tarefa_id=tarefa_id,
            nova_etapa=avancar.nova_etapa,
            usuario_id=usuario_id,
            usuario_nome=usuario_nome,
            acao=avancar.acao,
            db=db
        )
        return tarefa_atualizada
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@api_router.get("/tarefas/filtros", response_model=List[schemas.TarefaResponse])
def listar_tarefas_com_filtros(
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
    data_inicio: Optional[date_type] = None,
    data_fim: Optional[date_type] = None,
    db: Session = Depends(get_db)
):
    """Lista tarefas com filtros avançados."""
    return crud_tarefas.listar_tarefas_com_filtros(
        db=db,
        tipo_tarefa_id=tipo_tarefa_id,
        processo_id=processo_id,
        cliente_id=cliente_id,
        classe=classe,
        esfera_justica=esfera_justica,
        municipio_id=municipio_id,
        uf=uf,
        responsavel_id=responsavel_id,
        status=status,
        prazo_vencido=prazo_vencido,
        data_inicio=data_inicio,
        data_fim=data_fim
    )


@api_router.get("/tarefas/{tarefa_id}/derivadas", response_model=List[schemas.TarefaResponse])
def listar_tarefas_derivadas(tarefa_id: int, recursivo: bool = False, db: Session = Depends(get_db)):
    """Lista tarefas derivadas de uma tarefa."""
    tarefa = crud_tarefas.buscar_tarefa(tarefa_id, db)
    if not tarefa:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    
    return crud_tarefas.listar_tarefas_derivadas(tarefa, db, recursivo)


@api_router.get("/tarefas/estatisticas", response_model=schemas.EstatisticasTarefas)
def obter_estatisticas_tarefas(db: Session = Depends(get_db)):
    """Retorna estatísticas gerais sobre tarefas."""
    return crud_tarefas.obter_estatisticas_tarefas(db)


@api_router.get("/tarefas/metricas-responsavel", response_model=List[schemas.MetricasResponsavel])
def obter_metricas_responsavel(db: Session = Depends(get_db)):
    """Retorna métricas de tarefas por responsável."""
    return crud_tarefas.obter_metricas_responsavel(db)


@api_router.get("/tarefas/tempo-medio-tipo", response_model=List[schemas.TempoMedioPorTipo])
def obter_tempo_medio_por_tipo(db: Session = Depends(get_db)):
    """Retorna tempo médio de conclusão por tipo de tarefa."""
    return crud_tarefas.obter_tempo_medio_por_tipo(db)


# --- Pagamentos Pendentes (Sistema Simplificado) ---
from database import crud_pagamentos_pendentes

@api_router.get("/pagamentos-pendentes", response_model=List[schemas.PagamentoPendente])
def listar_pagamentos_pendentes(
    mes: Optional[int] = None,
    ano: Optional[int] = None,
    tipo: Optional[str] = None,
    socio_id: Optional[int] = None,
    apenas_pendentes: bool = False,
    db: Session = Depends(get_db)
):
    """Lista pagamentos pendentes com filtros opcionais"""
    return crud_pagamentos_pendentes.listar_pagamentos_pendentes(
        db, mes=mes, ano=ano, tipo=tipo, socio_id=socio_id, apenas_pendentes=apenas_pendentes
    )


@api_router.get("/pagamentos-pendentes/{pagamento_id}", response_model=schemas.PagamentoPendente)
def obter_pagamento_pendente(pagamento_id: int, db: Session = Depends(get_db)):
    """Obtém um pagamento pendente por ID"""
    pagamento = crud_pagamentos_pendentes.obter_pagamento_pendente(db, pagamento_id)
    if not pagamento:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    return pagamento


@api_router.post("/pagamentos-pendentes/{pagamento_id}/confirmar", response_model=schemas.PagamentoPendente)
def confirmar_pagamento(
    pagamento_id: int, 
    data_pagamento: schemas.ConfirmarPagamento,
    db: Session = Depends(get_db)
):
    """Confirma um pagamento pendente"""
    try:
        return crud_pagamentos_pendentes.confirmar_pagamento(
            db, pagamento_id, data_pagamento.data_confirmacao
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@api_router.post("/pagamentos-pendentes/{pagamento_id}/desconfirmar", response_model=schemas.PagamentoPendente)
def desconfirmar_pagamento(pagamento_id: int, db: Session = Depends(get_db)):
    """Remove a confirmação de um pagamento"""
    try:
        return crud_pagamentos_pendentes.desconfirmar_pagamento(db, pagamento_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@api_router.delete("/pagamentos-pendentes/{pagamento_id}")
def excluir_pagamento_pendente(pagamento_id: int, db: Session = Depends(get_db)):
    """Exclui um pagamento pendente"""
    sucesso = crud_pagamentos_pendentes.excluir_pagamento_pendente(db, pagamento_id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    return {"status": "ok"}


@api_router.get("/pagamentos-pendentes/resumo/{mes}/{ano}")
def obter_resumo_mes(mes: int, ano: int, db: Session = Depends(get_db)):
    """Retorna resumo financeiro do mês"""
    return crud_pagamentos_pendentes.obter_resumo_mes(db, mes, ano)


@api_router.get("/pagamentos-pendentes/socio/{socio_id}")
def obter_pendencias_socio(
    socio_id: int, 
    apenas_pendentes: bool = True, 
    db: Session = Depends(get_db)
):
    """Retorna todas as pendências de um sócio"""
    return crud_pagamentos_pendentes.obter_pendencias_por_socio(db, socio_id, apenas_pendentes)


@api_router.post("/pagamentos-pendentes/gerar/{mes}/{ano}")
def gerar_pendencias_mes_endpoint(
    mes: int = Path(..., ge=1, le=12),
    ano: int = Path(..., ge=2000),
    db: Session = Depends(get_db)
):
    """
    Gera pagamentos pendentes CONSOLIDADOS para um mês específico.
    
    Um único boleto de SIMPLES por mês, um único de INSS, etc.
    Baseado na DRE consolidada do mês.
    
    Este endpoint deve ser chamado após lançar todas as entradas do mês
    e consolidar a DRE.
    """
    try:
        pendencias = crud_pagamentos_pendentes.gerar_pendencias_mes(db, mes, ano)
        return {
            "status": "success",
            "mes": mes,
            "ano": ano,
            "total_pendencias": len(pendencias),
            "pendencias": pendencias
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Serve frontend static files from the repository root `frontend/` directory
frontend_build_dir = PathLib(__file__).resolve().parent.parent / "frontend" / "react-app" / "dist"

# Mount the 'assets' directory from the build output
if (frontend_build_dir / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_build_dir / "assets")), name="assets")


# register API router FIRST (before catch-all route)
app.include_router(api_router)
app.include_router(config_router)


@app.get("/")
def index():
    # prefer built react app in `frontend/dist/index.html` if available
    index_html = frontend_build_dir / "index.html"
    if index_html.exists():
        return FileResponse(str(index_html))
    return {"error": "Frontend not built. Run `npm run build` in `frontend/react-app`."}


# Catch-all route for React Router (must be last)
@app.get("/{full_path:path}")
def serve_react_app(full_path: str):
    # Don't serve index.html for API routes
    if full_path.startswith("api/") or full_path.startswith("config/"):
        return {"detail": "Not Found"}
    
    # Serve index.html for all other routes (React Router will handle them)
    index_html = frontend_build_dir / "index.html"
    if index_html.exists():
        return FileResponse(str(index_html))
    return {"error": "Frontend not built. Run `npm run build` in `frontend/react-app`."}
