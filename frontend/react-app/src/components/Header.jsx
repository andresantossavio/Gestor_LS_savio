import React from 'react'

export default function Header({ title }){
  return (
    <div style={{ padding: 10, borderBottom: '1px solid #ddd', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
      <div style={{ fontSize: '18px', fontWeight: 'bold' }}>{title}</div>
    </div>
  )
}
