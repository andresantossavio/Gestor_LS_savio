import React, { useEffect, useState } from 'react';

const apiBase = '/api';

// Componente do Formulário de Processo
export default function ProcessoForm({ processoParaEditar, onFormSubmit, onCancel }) {
  const isEditing = !!processoParaEditar?.id;

  // Se estiver editando, garante que os campos classe/sub_classe não sejam 'null'
  const processoInicial = isEditing ? { ...processoParaEditar, classe: processoParaEditar.classe || '', sub_classe: processoParaEditar.sub_classe || '' } : null;
  const initialState = isEditing ? { ...processoParaEditar } : {
    numero: '',
    autor: '',
    reu: '',
    uf: '',
    comarca: '',
    vara: '',
    fase: '',
    esfera_justica: '',
    categoria: '',
    tribunal_originario: '',
    tipo: '',
    status: '',
    data_abertura: '',
    classe: '',
    sub_classe: '',
    observacoes: '',
    cliente_id: ''
  };
  const [formData, setFormData] = useState(processoInicial || initialState);
  const [ufs, setUfs] = useState([]);
  const [tipos, setTipos] = useState([]);
  const [categorias, setCategorias] = useState([]);
  const [tribunais, setTribunais] = useState([]);
  const [esferas, setEsferas] = useState([]);
  const [clientes, setClientes] = useState([]);
  const [classes, setClasses] = useState({});

  useEffect(() => {
    const fetchConfigData = async () => {
      try {
        const [ufsRes, classesRes, tiposRes, categoriasRes, tribunaisRes, esferasRes, clientesRes] = await Promise.all([
          fetch('/api/config/ufs'),
          fetch('/api/config/classes'),
          fetch('/api/config/tipos'),
          fetch('/api/config/categorias'),
          fetch('/api/config/tribunais'),
          fetch('/api/config/esferas'),
          fetch('/api/clientes') // Busca a lista de clientes
        ]);
        setUfs(await ufsRes.json());
        setClasses(await classesRes.json());
        setTipos(await tiposRes.json());
        setCategorias(await categoriasRes.json());
        setTribunais(await tribunaisRes.json());
        setEsferas(await esferasRes.json());
        setClientes(await clientesRes.json()); // Armazena a lista de clientes no estado
      } catch (err) {
        console.error("Erro ao buscar dados de configuração:", err);
      }
    };
    fetchConfigData();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    const newFormData = { ...formData, [name]: value };

    // Se a categoria mudar para 'Originário'
    if (name === 'categoria' && value === 'Originário') {
      // Limpa os campos de 'Comum'
      newFormData.uf = '';
      newFormData.comarca = '';
      newFormData.vara = '';
      // Define o tipo como Judicial e limpa classe/sub-classe
      newFormData.tipo = 'Judicial';
      newFormData.classe = '';
      newFormData.sub_classe = '';
    }

    // Se a categoria mudar para 'Comum'
    if (name === 'categoria' && value === 'Comum') {
      // Limpa os campos de 'Originário' e reseta o tipo
      newFormData.tribunal_originario = '';
      newFormData.tipo = '';
    }

    // NOVA REGRA: Se a classe for Criminal, o tipo é sempre Judicial.
    if (name === 'classe' && value === 'Criminal') {
      newFormData.tipo = 'Judicial';
    }

    // Se o tipo mudar para algo que não seja Judicial, e a classe for Criminal, limpa a classe.
    if (name === 'tipo' && value !== 'Judicial' && newFormData.classe === 'Criminal') {
      newFormData.classe = '';
      newFormData.sub_classe = '';
    }

    // --- NOVAS REGRAS DE ESFERA AUTOMÁTICA ---
    // Se a classe for Trabalhista, a esfera é Trabalhista
    if (name === 'classe' && value === 'Trabalhista') {
      newFormData.esfera_justica = 'Justiça Trabalhista';
    }

    // Se a classe for Eleitoral, a esfera é Eleitoral
    if (name === 'classe' && value === 'Eleitoral') {
      newFormData.esfera_justica = 'Justiça Eleitoral';
    }

    // Regras baseadas no tribunal originário
    if (name === 'tribunal_originario') {
      if (value === 'TRT') newFormData.esfera_justica = 'Justiça Trabalhista';
      else if (value === 'TRF') newFormData.esfera_justica = 'Justiça Federal';
      else if (value === 'TRM') newFormData.esfera_justica = 'Justiça Militar';
      else if (value === 'TRE') newFormData.esfera_justica = 'Justiça Eleitoral';
      // Limpa a esfera se for um tribunal sem regra automática (STJ, STF, TJ)
      else if (['STJ', 'STF', 'TJ'].includes(value)) {
        newFormData.esfera_justica = '';
      }
    }

    // Se a categoria mudar, limpa a esfera para reavaliação
    if (name === 'categoria') {
      newFormData.esfera_justica = '';
    }

    // Se a classe mudar, limpa a esfera para reavaliação (exceto para as que tem regra)
    if (name === 'classe' && !['Trabalhista', 'Eleitoral'].includes(value)) {
      newFormData.esfera_justica = '';
    }

    // Se a classe ou sub-classe mudar, limpa a fase para reavaliação
    if (name === 'classe' || name === 'sub_classe') {
      newFormData.fase = '';
    }

    // Se o tribunal for TRF ou TJ e a classe for Trabalhista, limpa a classe
    if (name === 'tribunal_originario' && ['TRF', 'TJ'].includes(value) && newFormData.classe === 'Trabalhista') {
      newFormData.classe = '';
      newFormData.sub_classe = '';
    }

    setFormData(newFormData);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const url = isEditing ? `${apiBase}/processos/${processoParaEditar.id}` : `${apiBase}/processos`;
    const method = isEditing ? 'PUT' : 'POST';

    // Função para limpar o objeto de dados, removendo chaves com valores nulos ou vazios.
    // Isso evita enviar campos opcionais vazios que podem falhar na validação do backend (ex: Enums).
    const cleanData = (obj) => {
      const newObj = {};
      for (const key in obj) {
        if (obj[key] !== null && obj[key] !== '') {
          newObj[key] = obj[key];
        }
      }
      return newObj;
    };
    try {
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(cleanData(formData)),
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Falha ao salvar processo');
      }
      onFormSubmit();
    } catch (err) {
      console.error(err);
      alert(`Erro ao salvar processo: ${err.message}`);
    }
  };

  const subClasses = classes[formData.classe] || [];

  // Filtra as classes disponíveis com base no tipo selecionado
  let availableClasses = Object.keys(classes);

  // Regra 1: Se o tipo não for Judicial, remove a classe Criminal
  if (formData.tipo && formData.tipo !== 'Judicial') {
    availableClasses = availableClasses.filter(c => c !== 'Criminal');
  }

  // Regra 2: Se o tipo não for Judicial, remove a classe Eleitoral
  if (formData.tipo && formData.tipo !== 'Judicial') {
    availableClasses = availableClasses.filter(c => c !== 'Eleitoral');
  }
  // Regra 2: Se for Originário de TRF ou TJ, remove a classe Trabalhista
  if (formData.categoria === 'Originário' && ['TRF', 'TJ'].includes(formData.tribunal_originario)) {
    availableClasses = availableClasses.filter(c => c !== 'Trabalhista');
  }

  // --- LÓGICA DE EXIBIÇÃO DA ESFERA DE JUSTIÇA ---

  // 1. Filtra as esferas disponíveis com base nas regras
  let availableEsferas = [...esferas];

  // Regra da Esfera Militar: só aparece se a classe for Criminal
  if (formData.classe !== 'Criminal') {
    availableEsferas = availableEsferas.filter(e => e !== 'Justiça Militar');
  }

  // Regra da Esfera Trabalhista: só aparece nos cenários corretos
  const isComumTrabalhista = formData.categoria === 'Comum' && formData.tipo === 'Judicial' && formData.classe === 'Trabalhista';
  const isOriginarioTrabalhista = formData.categoria === 'Originário' && ['TRT', 'STJ', 'STF'].includes(formData.tribunal_originario);
  if (!isComumTrabalhista && !isOriginarioTrabalhista) {
    availableEsferas = availableEsferas.filter(e => e !== 'Justiça Trabalhista');
  }

  // Regra da Esfera Eleitoral
  const isComumEleitoral = formData.categoria === 'Comum' && formData.tipo === 'Judicial' && formData.classe === 'Eleitoral';
  const isOriginarioEleitoral = formData.categoria === 'Originário' && formData.tribunal_originario === 'TRE';
  if (!isComumEleitoral && !isOriginarioEleitoral) {
    availableEsferas = availableEsferas.filter(e => e !== 'Justiça Eleitoral');
  }

  // 2. Define se o campo de seleção manual da Esfera deve ser exibido
  const deveExibirEsfera = (
    // Cenário Comum
    (formData.categoria === 'Comum' && formData.tipo === 'Judicial' && ['Cível', 'Criminal', 'Tributário', 'Previdenciário', 'Empresarial'].includes(formData.classe)) ||
    // Cenário Originário
    (formData.categoria === 'Originário' && ['STJ', 'STF', 'TJ'].includes(formData.tribunal_originario))
  );

  // --- LÓGICA DE EXIBIÇÃO DAS FASES ---
  // Começa com as fases padrão, sem "Arquivado"
  let availablePhases = ["Inicial", "Recursal"];
  const classesParaCumprimento = ['Cível', 'Trabalhista', 'Tributário', 'Empresarial', 'Previdenciário'];

  // Regra para "Cumprimento de Sentença"
  if (
    classesParaCumprimento.includes(formData.classe) ||
    formData.sub_classe === 'Eleitoral Cível'
  ) {
    availablePhases.push("Cumprimento de Sentença");
  }

  // Regra para "Execução da Pena"
  if (formData.classe === 'Criminal' || formData.sub_classe === 'Eleitoral Criminal') {
    availablePhases.push("Execução da Pena");
  }

  // Garante que "Arquivado" seja sempre a última opção da lista
  availablePhases.push("Arquivado");


  return (
    <div style={{ border: '1px solid #ccc', padding: '20px', margin: '20px 0' }}>
      <h3>{isEditing ? 'Editar Processo' : 'Novo Processo'}</h3>
      <form onSubmit={handleSubmit} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
        <input name="numero" value={formData.numero} onChange={handleChange} placeholder="Número do Processo" />
        <input name="autor" value={formData.autor} onChange={handleChange} placeholder="Autor" />
        <input name="reu" value={formData.reu} onChange={handleChange} placeholder="Réu" />
        <select name="categoria" value={formData.categoria} onChange={handleChange}>
          <option value="">Selecione a Categoria</option>
          {categorias.map(cat => <option key={cat} value={cat}>{cat}</option>)}
        </select>

        {/* Campos para Processo Originário */}
        {formData.categoria === 'Originário' && (
          <select name="tribunal_originario" value={formData.tribunal_originario} onChange={handleChange}>
            <option value="">Selecione o Tribunal</option>
            {tribunais.map(t => <option key={t} value={t}>{t}</option>)}
          </select>
        )}

        {/* Campos de Classe/Sub-classe para Tribunais específicos em Originário */}
        {formData.categoria === 'Originário' && ['STJ', 'STF', 'TJ', 'TRF'].includes(formData.tribunal_originario) && (
          <>
            <select name="classe" value={formData.classe} onChange={handleChange}>
              <option value="">Selecione a Classe</option>
              {availableClasses.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
            {subClasses.length > 0 && (
              <select name="sub_classe" value={formData.sub_classe} onChange={handleChange}><option value="">Selecione a Sub-classe</option>{subClasses.map(sub => <option key={sub} value={sub}>{sub}</option>)}</select>
            )}
          </>
        )}

        {/* Campos para Processo Comum */}
        {formData.categoria === 'Comum' && (
          <>
            <select name="uf" value={formData.uf} onChange={handleChange}>
              <option value="">Selecione a UF</option>
              {ufs.map(uf => <option key={uf} value={uf}>{uf}</option>)}
            </select>
            <select name="tipo" value={formData.tipo} onChange={handleChange} disabled={formData.classe === 'Criminal'}>
              <option value="">Selecione o Tipo</option>
              {tipos.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
            <input name="comarca" value={formData.comarca} onChange={handleChange} placeholder="Comarca" />
            <input name="vara" value={formData.vara} onChange={handleChange} placeholder="Vara/Juízo" />
            <select name="classe" value={formData.classe} onChange={handleChange}>
              <option value="">Selecione a Classe</option>
              {availableClasses.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
            {subClasses.length > 0 && (
              <select name="sub_classe" value={formData.sub_classe} onChange={handleChange}>
                <option value="">Selecione a Sub-classe</option>
                {subClasses.map(sub => <option key={sub} value={sub}>{sub}</option>)}
              </select>
            )}

            {/* Campo condicional para Esfera de Justiça */}
            {deveExibirEsfera && (
              <select name="esfera_justica" value={formData.esfera_justica} onChange={handleChange}>
                <option value="">Selecione a Esfera de Justiça</option>
                {availableEsferas.map(e => <option key={e} value={e}>{e}</option>)}
              </select>
            )}
          </>
        )}

        <select name="fase" value={formData.fase} onChange={handleChange}>
          <option value="">Selecione a Fase</option>
          {availablePhases.map(f => <option key={f} value={f}>{f}</option>)}
        </select>
        <select name="status" value={formData.status} onChange={handleChange}>
          <option value="">Selecione o Status</option>
          <option value="Ativo">Ativo</option>
          <option value="Encerrado">Encerrado</option>
        </select>
        <div>
          <label htmlFor="data_abertura" style={{ fontSize: '0.9em', color: '#555' }}>
            Data da Distribuição
          </label>
          <input id="data_abertura" name="data_abertura" value={formData.data_abertura} onChange={handleChange} type="date" style={{ width: '100%', boxSizing: 'border-box' }} />
        </div>
        <select name="cliente_id" value={formData.cliente_id} onChange={handleChange} style={{ gridColumn: '1 / -1' }}>
          <option value="">Selecione um Cliente</option>
          {clientes.map(cliente => (
            <option key={cliente.id} value={cliente.id}>{cliente.nome} (CPF/CNPJ: {cliente.cpf_cnpj})</option>
          ))}
        </select>
        <textarea name="observacoes" value={formData.observacoes} onChange={handleChange} placeholder="Observações" style={{ gridColumn: '1 / -1', minHeight: '80px' }} />
        <div>
          <button type="submit">Salvar</button>
          <button type="button" onClick={onCancel} style={{ marginLeft: '10px' }}>Cancelar</button>
        </div>
      </form>
    </div>
  );
}
