import React, { useEffect, useState, useCallback } from 'react'
import Header from '../components/Header'

const apiBase = '/api';

// Componente do Formulário de Cliente
function ClienteForm({ clienteParaEditar, onFormSubmit, onCancel }) {
  const inputStyle = { display: 'block', marginBottom: '10px', width: '100%', maxWidth: '500px', padding: '8px', borderRadius: '6px', border: '1px solid #d1d5db', fontSize: '14px' };
  
  const [formData, setFormData] = useState({
    nome: '',
    cpf_cnpj: '',
    telefone: '',
    email: '',
    capacidade: '',
    responsavel_nome: '',
    responsavel_cpf: '',
    nome_fantasia: '',
    tipo_pessoa: '',
    tipo_pj: '',
    subtipo_pj: '',
    cep: '',
    logradouro: '',
    numero: '',
    complemento: '',
    bairro: '',
    cidade: '',
    uf: '',
    ...clienteParaEditar
  });

  const [ufs, setUfs] = useState([]);

  useEffect(() => {
    const fetchUfs = async () => {
        try {
            const res = await fetch(`${apiBase}/config/ufs`);
            if (!res.ok) throw new Error('Falha ao buscar UFs');
            setUfs(await res.json());
        } catch (err) {
            console.error("Erro ao buscar UFs:", err);
        }
    };
    fetchUfs();
  }, []);

  const isEditing = !!clienteParaEditar?.id;

  const handleChange = (e) => {
    const { name, value } = e.target;
    const newFormData = { ...formData, [name]: value };

    // Limpa os sub-campos se o campo pai for alterado
    if (name === 'tipo_pessoa') {
      newFormData.tipo_pj = '';
      newFormData.subtipo_pj = '';
      newFormData.nome_fantasia = '';
      newFormData.capacidade = '';
      newFormData.responsavel_nome = '';
      newFormData.responsavel_cpf = '';
    }

    // Limpa os campos do responsável se a capacidade mudar para "Capaz"
    if (name === 'capacidade' && value === 'Capaz') {
      newFormData.responsavel_nome = '';
      newFormData.responsavel_cpf = '';
    }
    setFormData(newFormData);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const url = isEditing ? `${apiBase}/clientes/${clienteParaEditar.id}` : `${apiBase}/clientes`;
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
      delete newObj.id; // Remove o id que não faz parte do schema de criação/atualização
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
        throw new Error(errorData.detail || 'Falha ao salvar cliente');
      }
      onFormSubmit();
    } catch (err) {
      console.error(err);
      alert(`Erro ao salvar cliente: ${err.message}`);
    }
  };

  const subtiposPjPublico = ["Ente Federativo", "Fundação", "Autarquia"];
  const subtiposPjPrivado = ["MEI", "EI", "LTDA", "SLU", "Sociedade Simples", "S/A", "SAF", "Associação", "Cooperativa", "Fundação", "Autarquia"];

  return (
    <div className="card" style={{ marginTop: '20px' }}>
      <h3 style={{ marginTop: 0, marginBottom: '20px', color: '#374151' }}>{isEditing ? 'Editar Cliente' : 'Novo Cliente'}</h3>
      <form onSubmit={handleSubmit}>
        <select name="tipo_pessoa" value={formData.tipo_pessoa} onChange={handleChange} required style={inputStyle}>
          <option value="">Selecione o Tipo de Pessoa</option>
          <option value="Pessoa Física">Pessoa Física</option>
          <option value="Pessoa Jurídica">Pessoa Jurídica</option>
        </select>

        {/* Campos para Pessoa Jurídica */}
        {formData.tipo_pessoa === 'Pessoa Jurídica' && (
          <>
            <select name="tipo_pj" value={formData.tipo_pj} onChange={handleChange} required style={inputStyle}>
              <option value="">Selecione o Tipo de PJ</option>
              <option value="Direito Público">PJ de Direito Público</option>
              <option value="Direito Privado">PJ de Direito Privado</option>
            </select>

            {formData.tipo_pj === 'Direito Público' && (
              <select name="subtipo_pj" value={formData.subtipo_pj} onChange={handleChange} required style={inputStyle}>
                <option value="">Selecione o Subtipo</option>
                {subtiposPjPublico.map(sub => <option key={sub} value={sub}>{sub}</option>)}
              </select>
            )}

            {formData.tipo_pj === 'Direito Privado' && (
              <select name="subtipo_pj" value={formData.subtipo_pj} onChange={handleChange} required style={inputStyle}>
                <option value="">Selecione o Subtipo</option>
                {subtiposPjPrivado.map(sub => <option key={sub} value={sub}>{sub}</option>)}
              </select>
            )}

            {/* Campo Nome Fantasia para PJ de Direito Privado */}
            {formData.tipo_pj === 'Direito Privado' && (
              <input name="nome_fantasia" value={formData.nome_fantasia} onChange={handleChange} placeholder="Nome Fantasia" style={inputStyle} />
            )}

          </>
        )}

        {/* Campos Comuns (aparecem após a seleção inicial) */}
        {formData.tipo_pessoa === 'Pessoa Física' && (
          <>
            <select name="capacidade" value={formData.capacidade} onChange={handleChange} required style={inputStyle}>
              <option value="">Selecione a Capacidade</option>
              <option value="Capaz">Pessoa Capaz</option>
              <option value="Relativamente Incapaz">Relativamente Incapaz</option>
              <option value="Incapaz">Incapaz</option>
            </select>

            {['Relativamente Incapaz', 'Incapaz'].includes(formData.capacidade) && (
              <>
                <input name="responsavel_nome" value={formData.responsavel_nome} onChange={handleChange} placeholder="Nome do Responsável Legal" required style={inputStyle} />
                <input name="responsavel_cpf" value={formData.responsavel_cpf} onChange={handleChange} placeholder="CPF do Responsável Legal" required style={inputStyle} />
              </>
            )}
          </>
        )}

        {formData.tipo_pessoa && (
          <>
            <input name="nome" value={formData.nome} onChange={handleChange} placeholder={formData.tipo_pessoa === 'Pessoa Física' ? 'Nome Completo' : 'Razão Social'} required style={inputStyle} />
            <input name="cpf_cnpj" value={formData.cpf_cnpj} onChange={handleChange} placeholder={formData.tipo_pessoa === 'Pessoa Física' ? 'CPF' : 'CNPJ'} required style={inputStyle} />
            <input name="telefone" value={formData.telefone} onChange={handleChange} placeholder="Telefone" style={inputStyle} />
            <input type="email" name="email" value={formData.email} onChange={handleChange} placeholder="Email" style={inputStyle} />
            <input name="cep" value={formData.cep} onChange={handleChange} placeholder="CEP" style={inputStyle} />
            <input name="logradouro" value={formData.logradouro} onChange={handleChange} placeholder="Logradouro (Rua, Av.)" style={inputStyle} />
            <input name="numero" value={formData.numero} onChange={handleChange} placeholder="Número" style={inputStyle} />
            <input name="complemento" value={formData.complemento} onChange={handleChange} placeholder="Complemento (Apto, Bloco)" style={inputStyle} />
            <input name="bairro" value={formData.bairro} onChange={handleChange} placeholder="Bairro" style={inputStyle} />
            <input name="cidade" value={formData.cidade} onChange={handleChange} placeholder="Cidade" style={inputStyle} />
            <select name="uf" value={formData.uf} onChange={handleChange} style={inputStyle}>
              <option value="">Selecione a UF</option>
              {ufs.map(uf => <option key={uf} value={uf}>{uf}</option>)}
            </select>
          </>
        )}

        <div style={{ marginTop: '20px' }}>
          <button type="submit" className="btn btn-primary">Salvar</button>
          <button type="button" onClick={onCancel} className="btn btn-secondary" style={{ marginLeft: '10px' }}>Cancelar</button>
        </div>
      </form>
    </div>
  );
}

export default function Clientes() {
  const [clientes, setClientes] = useState([])
  const [exibirForm, setExibirForm] = useState(false);
  const [clienteParaEditar, setClienteParaEditar] = useState(null);

  const load = useCallback(async () => {
    try {
      const res = await fetch(`${apiBase}/clientes`);
      if (!res.ok) throw new Error(`Erro na API: ${res.status}`);
      const json = await res.json();
      setClientes(json);
    } catch (err) {
      console.error(err);
    }
  }, []); // useCallback com array de dependências vazio

  useEffect(() => { load() }, [load])

  const handleEdit = (cliente) => {
    setClienteParaEditar(cliente);
    setExibirForm(true);
  };

  const handleDelete = async (clienteId) => {
    if (window.confirm('Tem certeza que deseja excluir este cliente?')) {
      try {
        await fetch(`${apiBase}/clientes/${clienteId}`, { method: 'DELETE' });
        load();
      } catch (err) {
        console.error(err);
        alert('Falha ao excluir cliente.');
      }
    }
  };

  return (
    <div className="content">
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <Header title="Clientes" />
          {!exibirForm && (
            <button onClick={() => { setClienteParaEditar(null); setExibirForm(true); }} className="btn btn-primary">
              + Novo Cliente
            </button>
          )}
        </div>
      </div>

      {exibirForm && <ClienteForm
        clienteParaEditar={clienteParaEditar}
        onFormSubmit={() => { setExibirForm(false); load(); }}
        onCancel={() => setExibirForm(false)}
      />}

      {!exibirForm && (
        <div className="card">
          {clientes.length === 0 && <p style={{ textAlign: 'center', color: '#6b7280' }}>Nenhum cliente cadastrado</p>}
          {clientes.length > 0 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {clientes.map(c => (
                <div key={c.id} style={{ padding: '16px', backgroundColor: '#f9fafb', borderRadius: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', transition: 'all 0.2s' }}>
                  <div>
                    <div style={{ fontWeight: '600', color: '#374151', marginBottom: '4px' }}>
                      {c.nome}
                      {c.nome_fantasia && <span style={{ color: '#6b7280', fontWeight: '400' }}> ({c.nome_fantasia})</span>}
                    </div>
                    <div style={{ color: '#6b7280', fontSize: '14px' }}>
                      {c.cpf_cnpj} • {c.cidade}/{c.uf}
                    </div>
                  </div>
                  <div>
                    <button onClick={() => window.location.href = `/clientes/${c.id}`} className="btn btn-primary" style={{ marginRight: '8px', padding: '6px 12px', fontSize: '13px' }}>Ver Detalhes</button>
                    <button onClick={() => handleEdit(c)} className="btn btn-primary" style={{ marginRight: '8px', padding: '6px 12px', fontSize: '13px' }}>Editar</button>
                    <button onClick={() => handleDelete(c.id)} className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: '13px' }}>Excluir</button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
