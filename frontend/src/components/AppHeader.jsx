import { NavLink } from 'react-router-dom'
import Brand from './Brand'

export default function AppHeader() {
  return (
    <header className="app-header">
      <Brand compact />
      <nav className="app-nav" aria-label="Navegação principal">
        <NavLink to="/" end>Início</NavLink>
        <NavLink to="/chat">Assistente</NavLink>
        <NavLink to="/operations">Operações</NavLink>
      </nav>
      <span className="environment-pill">PORTFÓLIO · DEMO</span>
    </header>
  )
}
