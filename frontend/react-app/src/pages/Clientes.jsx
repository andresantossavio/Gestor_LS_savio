import React, { useEffect, useState, useCallback } from 'react'
import Header from '../components/Header'

const apiBase = '/api';

// Componente do Formulário de Cliente
function ClienteForm({ clienteParaEditar, onFormSubmit, onCancel }) {
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

    try {
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
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
    <div style={{ border: '1px solid #ccc', padding: '20px', margin: '20px 0' }}>
      <h3>{isEditing ? 'Editar Cliente' : 'Novo Cliente'}</h3>
      <form onSubmit={handleSubmit}>
        <select name="tipo_pessoa" value={formData.tipo_pessoa} onChange={handleChange} required style={{ display: 'block', marginBottom: '10px', width: '300px' }}>
          <option value="">Selecione o Tipo de Pessoa</option>
          <option value="Pessoa Física">Pessoa Física</option>
          <option value="Pessoa Jurídica">Pessoa Jurídica</option>
        </select>

        {/* Campos para Pessoa Jurídica */}
        {formData.tipo_pessoa === 'Pessoa Jurídica' && (
          <>
            <select name="tipo_pj" value={formData.tipo_pj} onChange={handleChange} required style={{ display: 'block', marginBottom: '10px', width: '300px' }}>
              <option value="">Selecione o Tipo de PJ</option>
              <option value="Direito Público">PJ de Direito Público</option>
              <option value="Direito Privado">PJ de Direito Privado</option>
            </select>

            {formData.tipo_pj === 'Direito Público' && (
              <select name="subtipo_pj" value={formData.subtipo_pj} onChange={handleChange} required style={{ display: 'block', marginBottom: '10px', width: '300px' }}>
                <option value="">Selecione o Subtipo</option>
                {subtiposPjPublico.map(sub => <option key={sub} value={sub}>{sub}</option>)}
              </select>
            )}

            {formData.tipo_pj === 'Direito Privado' && (
              <select name="subtipo_pj" value={formData.subtipo_pj} onChange={handleChange} required style={{ display: 'block', marginBottom: '10px', width: '300px' }}>
                <option value="">Selecione o Subtipo</option>
                {subtiposPjPrivado.map(sub => <option key={sub} value={sub}>{sub}</option>)}
              </select>
            )}

            {/* Campo Nome Fantasia para PJ de Direito Privado */}
            {formData.tipo_pj === 'Direito Privado' && (
              <input name="nome_fantasia" value={formData.nome_fantasia} onChange={handleChange} placeholder="Nome Fantasia" style={{ display: 'block', marginBottom: '10px', width: '300px' }} />
            )}

          </>
        )}

        {/* Campos Comuns (aparecem após a seleção inicial) */}
        {formData.tipo_pessoa === 'Pessoa Física' && (
          <>
            <select name="capacidade" value={formData.capacidade} onChange={handleChange} required style={{ display: 'block', marginBottom: '10px', width: '300px' }}>
              <option value="">Selecione a Capacidade</option>
              <option value="Capaz">Pessoa Capaz</option>
              <option value="Relativamente Incapaz">Relativamente Incapaz</option>
              <option value="Incapaz">Incapaz</option>
            </select>

            {['Relativamente Incapaz', 'Incapaz'].includes(formData.capacidade) && (
              <>
                <input name="responsavel_nome" value={formData.responsavel_nome} onChange={handleChange} placeholder="Nome do Responsável Legal" required style={{ display: 'block', marginBottom: '10px', width: '300px' }} />
                <input name="responsavel_cpf" value={formData.responsavel_cpf} onChange={handleChange} placeholder="CPF do Responsável Legal" required style={{ display: 'block', marginBottom: '10px', width: '300px' }} />
              </>
            )}
          </>
        )}

        {formData.tipo_pessoa && (
          <>
            <input name="nome" value={formData.nome} onChange={handleChange} placeholder={formData.tipo_pessoa === 'Pessoa Física' ? 'Nome Completo' : 'Razão Social'} required style={{ display: 'block', marginBottom: '10px', width: '300px' }} />
            <input name="cpf_cnpj" value={formData.cpf_cnpj} onChange={handleChange} placeholder={formData.tipo_pessoa === 'Pessoa Física' ? 'CPF' : 'CNPJ'} required style={{ display: 'block', marginBottom: '10px', width: '300px' }} />
            <input name="telefone" value={formData.telefone} onChange={handleChange} placeholder="Telefone" style={{ display: 'block', marginBottom: '10px', width: '300px' }} />
            <input type="email" name="email" value={formData.email} onChange={handleChange} placeholder="Email" style={{ display: 'block', marginBottom: '10px', width: '300px' }} />
            <input name="cep" value={formData.cep} onChange={handleChange} placeholder="CEP" style={{ display: 'block', marginBottom: '10px', width: '300px' }} />
            <input name="logradouro" value={formData.logradouro} onChange={handleChange} placeholder="Logradouro (Rua, Av.)" style={{ display: 'block', marginBottom: '10px', width: '300px' }} />
            <input name="numero" value={formData.numero} onChange={handleChange} placeholder="Número" style={{ display: 'block', marginBottom: '10px', width: '300px' }} />
            <input name="complemento" value={formData.complemento} onChange={handleChange} placeholder="Complemento (Apto, Bloco)" style={{ display: 'block', marginBottom: '10px', width: '300px' }} />
            <input name="bairro" value={formData.bairro} onChange={handleChange} placeholder="Bairro" style={{ display: 'block', marginBottom: '10px', width: '300px' }} />
            <input name="cidade" value={formData.cidade} onChange={handleChange} placeholder="Cidade" style={{ display: 'block', marginBottom: '10px', width: '300px' }} />
            <input name="uf" value={formData.uf} onChange={handleChange} placeholder="UF" maxLength="2" style={{ display: 'block', marginBottom: '10px', width: '300px' }} />
          </>
        )}

        <button type="submit">Salvar</button>
        <button type="button" onClick={onCancel} style={{ marginLeft: '10px' }}>Cancelar</button>
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
      const res = await fetch('/api/clientes');
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
    <div style={{ padding: 20 }}>
      <Header title="Clientes" />
      {!exibirForm && <button onClick={() => { setClienteParaEditar(null); setExibirForm(true); }}>Novo Cliente</button>}
      {exibirForm && <ClienteForm
        clienteParaEditar={clienteParaEditar}
        onFormSubmit={() => { setExibirForm(false); load(); }}
        onCancel={() => setExibirForm(false)}
      />}
      <div style={{ marginTop: 20 }}>
        {clientes.length === 0 && <div>Nenhum cliente</div>}
        {clientes.map(c => (
          <div key={c.id} style={{ borderBottom: '1px solid #ddd', padding: 10 }}>
            <strong>{c.nome}</strong> 
            {c.nome_fantasia && ` (${c.nome_fantasia})`}
            — {c.cpf_cnpj} — {c.cidade}/{c.uf}
            <button onClick={() => handleEdit(c)} style={{ marginLeft: '20px' }}>Editar</button>
            <button onClick={() => handleDelete(c.id)} style={{ marginLeft: '10px' }}>Excluir</button>
          </div>
        ))}
      </div>
    </div>
  )
}
