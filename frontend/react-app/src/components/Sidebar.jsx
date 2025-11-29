import React, { useState } from 'react';
import { NavLink, useNavigate, useLocation } from 'react-router-dom';

const menuItems = [
    { name: 'Dashboard', to: '/', icon: '📊' },
    { name: 'Cadastros', to: '/cadastros', icon: '📝' },
    { name: 'Processos', to: '/processos', icon: '⚖️' },
    {
        name: 'Contabilidade',
        to: '/contabilidade',
        icon: '💰'
    },
    { name: 'Tarefas', to: '/tarefas', icon: '✅' },
    { name: 'Clientes', to: '/clientes', icon: '👤' },
    { name: 'Configurações', to: '/config', icon: '⚙️' }
];

const SubMenuItem = ({ subItem, isActive, onClick }) => {
    const [hover, setHover] = useState(false);
    return (
        <div
            onClick={onClick}
            onMouseEnter={() => setHover(true)}
            onMouseLeave={() => setHover(false)}
            style={{
                display: 'block',
                padding: '10px 14px',
                margin: '4px 0',
                borderRadius: '8px',
                color: isActive ? '#000000' : (hover ? '#92400e' : '#6b7280'),
                textDecoration: 'none',
                fontSize: '13px',
                fontWeight: isActive ? '600' : '500',
                backgroundColor: isActive ? '#FFC107' : (hover ? '#fef3c7' : '#ffffff'),
                border: isActive ? '1px solid #FFA000' : '1px solid #e5e7eb',
                boxShadow: isActive ? '0 2px 4px rgba(255, 193, 7, 0.3)' : '0 1px 2px rgba(0, 0, 0, 0.03)',
                cursor: 'pointer',
                transition: 'all 0.2s ease-in-out'
            }}
        >
            <span style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                {subItem.icon && <span style={{ fontSize: '16px' }}>{subItem.icon}</span>}
                <span>{subItem.name}</span>
            </span>
        </div>
    );
};

const MenuItem = ({ item }) => {
    const navigate = useNavigate();
    const location = useLocation();
    const [isHovered, setIsHovered] = useState(false);
    const isActive = location.pathname === item.to;

    const baseStyle = {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '14px 16px',
        margin: '6px 0',
        borderRadius: '10px',
        color: isActive ? '#000000' : '#374151',
        background: isActive ? 'linear-gradient(135deg, #FFC107 0%, #FFB300 100%)' : '#f9fafb',
        textDecoration: 'none',
        fontWeight: isActive ? '700' : '600',
        fontSize: '14px',
        border: isActive ? '1px solid #FFA000' : '1px solid #e5e7eb',
        boxShadow: isActive ? '0 3px 6px rgba(255, 193, 7, 0.4)' : '0 1px 2px rgba(0, 0, 0, 0.05)',
        transition: 'all 0.2s ease-in-out',
        cursor: 'pointer'
    };

    const hoverStyle = {
        ...baseStyle,
        background: isActive ? 'linear-gradient(135deg, #FFC107 0%, #FFB300 100%)' : '#ffffff',
        color: isActive ? '#000000' : '#1f2937',
        border: '1px solid #FFC107',
        transform: 'translateY(-1px)',
        boxShadow: '0 4px 8px rgba(255, 193, 7, 0.2)'
    };

    return (
        <div>
            {item.to === '/contabilidade' ? (
                <a
                    href="/contabilidade"
                    style={{ ...(isHovered ? hoverStyle : baseStyle), display: 'flex', textDecoration: 'none' }}
                    onMouseEnter={() => setIsHovered(true)}
                    onMouseLeave={() => setIsHovered(false)}
                >
                    <span style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        {item.icon && <span style={{ fontSize: '18px' }}>{item.icon}</span>}
                        <span>{item.name}</span>
                    </span>
                </a>
            ) : (
                <div
                    role="button"
                    style={isHovered ? hoverStyle : baseStyle}
                    onMouseEnter={() => setIsHovered(true)}
                    onMouseLeave={() => setIsHovered(false)}
                    onClick={() => {
                        try {
                            console.debug('[Sidebar] Click nav item:', item.name, '->', item.to);
                        } catch (_) { /* noop */ }
                        navigate(item.to);
                    }}
                >
                    <span style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        {item.icon && <span style={{ fontSize: '18px' }}>{item.icon}</span>}
                        <span>{item.name}</span>
                    </span>
                </div>
            )}
            
            
        </div>
    );
};

export default function Sidebar() {
    return (
        <aside style={{
            width: '260px',
            background: '#ffffff',
            color: '#1f2937',
            padding: 0,
            boxSizing: 'border-box',
            borderRight: '1px solid #e5e7eb',
            boxShadow: '2px 0 8px rgba(0, 0, 0, 0.06)',
            display: 'flex',
            flexDirection: 'column',
            height: '100vh',
            position: 'relative',
            zIndex: 1000,
            pointerEvents: 'auto'
        }}>
            <div style={{
                fontSize: '18px',
                fontWeight: '700',
                marginBottom: 0,
                color: '#1f2937',
                textAlign: 'center',
                padding: '24px 20px',
                background: '#ffffff',
                borderBottom: '2px solid #f3f4f6'
            }}>
                <div style={{ fontSize: '20px', fontWeight: '700', color: '#1f2937' }}>GESTOR LS</div>
                <div style={{ fontSize: '12px', fontWeight: '400', color: '#6b7280', marginTop: '6px' }}>Leão & Savio Advogados</div>
            </div>
            <nav style={{ padding: '16px 12px', flex: 1, overflowY: 'auto' }}>
                {menuItems.map(item => (
                    <MenuItem key={item.name} item={item} />
                ))}
            </nav>
        </aside>
    );
}
