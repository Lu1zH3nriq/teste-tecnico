import React from 'react';
import { useAuth } from '../../context/AuthContext';
import './ToDoList.css';

function DashboardPage() {
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <div className="dashboard-header-content">
          <h1>To-Do List</h1>
          <div className="user-info">
            <span>Olá, {user?.first_name || 'Usuário'}!</span>
            <button onClick={handleLogout} className="logout-button">
              Sair
            </button>
          </div>
        </div>
      </header>

      <main className="dashboard-main">
        <div className="welcome-section">
          <h2>🎉 Bem-vindo ao Sistema de Tarefas!</h2>
          <p>
            Você está logado com sucesso. Aqui você poderá gerenciar suas tarefas,
            visualizar estatísticas e muito mais.
          </p>
          
          <div className="feature-cards">
            <div className="feature-card">
              <div className="feature-icon">📝</div>
              <h3>Gerenciar Tarefas</h3>
              <p>Crie, edite e organize suas tarefas de forma eficiente</p>
              <span className="feature-status">Em breve</span>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">📊</div>
              <h3>Dashboard</h3>
              <p>Visualize estatísticas e métricas das suas tarefas</p>
              <span className="feature-status">Em breve</span>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">🔍</div>
              <h3>Filtros</h3>
              <p>Encontre tarefas rapidamente com filtros avançados</p>
              <span className="feature-status">Em breve</span>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default DashboardPage;
