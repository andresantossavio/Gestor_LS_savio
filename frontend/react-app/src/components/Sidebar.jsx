import React, { useState } from 'react';
import { Link, NavLink } from 'react-router-dom';

const menuItems = [
    { name: 'Dashboard', to: '/' },
    { name: 'Cadastros', to: '/cadastros' },
    { name: 'Processos', to: '/processos' },
    {
        name: 'Contabilidade',
        to: '/contabilidade',
        subItems: [
            { name: 'Nova Entrada', to: '/contabilidade/entradas/nova' },
            { name: 'Nova Despesa', to: '/contabilidade/despesas/nova' },
            { name: 'Gerenciar Sócios', to: '/contabilidade/socios' },
        ]
    },
    { name: 'Tarefas', to: '/tarefas' },
    { name: 'Clientes', to: '/clientes' },
    { name: 'Configurações', to: '/config' }
];

const MenuItem = ({ item }) => {
    const [isSubMenuOpen, setIsSubMenuOpen] = useState(false);
    const hasSubItems = item.subItems && item.subItems.length > 0;

    // Alterna o submenu apenas se houver sub-itens
    const toggleSubMenu = (e) => {
        if (hasSubItems) {
            e.preventDefault(); // Previne a navegação da NavLink principal
            setIsSubMenuOpen(!isSubMenuOpen);
        }
    };

    return (
        <div>
            <NavLink
                to={item.to}
                className="menu-item"
                onClick={toggleSubMenu}
            >
                {item.name}
                {hasSubItems && <span className="submenu-arrow">{isSubMenuOpen ? '▲' : '▼'}</span>}
            </NavLink>
            {hasSubItems && isSubMenuOpen && (
                <div className="submenu">
                    {item.subItems.map(subItem => (
                        <NavLink
                            key={subItem.to}
                            to={subItem.to}
                            className="submenu-item"
                        >
                            {subItem.name}
                        </NavLink>
                    ))}
                </div>
            )}
        </div>
    );
};

export default function Sidebar() {
    return (
        <aside className="sidebar">
            <div className="logo">Gestão Leão e Savio</div>
            <nav>
                {menuItems.map(item => (
                    <MenuItem key={item.name} item={item} />
                ))}
            </nav>
        </aside>
    );
}
