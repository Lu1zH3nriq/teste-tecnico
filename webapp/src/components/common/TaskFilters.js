import React, { useState, useEffect } from 'react';
import { FiSearch, FiFilter, FiX, FiClock } from 'react-icons/fi';
import './TaskFilters.css';

const TaskFilters = ({
  filters = {},
  onFiltersChange,
  onClearFilters,
  loading = false
}) => {
  
  // Estado local para os filtros antes de aplicar
  const [localFilters, setLocalFilters] = useState(filters);

  // Sincronizar quando os filtros externos mudarem (ex: limpar filtros)
  useEffect(() => {
    setLocalFilters(filters);
  }, [filters]);

  const statusOptions = [
    { value: '', label: 'Todos os Status' },
    { value: 'pending', label: 'Pendente' },
    { value: 'in_progress', label: 'Em Progresso' },
    { value: 'completed', label: 'Concluído' },
    { value: 'cancelled', label: 'Cancelado' }
  ];

  const priorityOptions = [
    { value: '', label: 'Todas as Prioridades' },
    { value: 'low', label: 'Baixa' },
    { value: 'medium', label: 'Média' },
    { value: 'high', label: 'Alta' },
    { value: 'urgent', label: 'Urgente' }
  ];

  const orderingOptions = [
    { value: '-created_at', label: 'Mais Recentes' },
    { value: 'created_at', label: 'Mais Antigas' },
    { value: 'title', label: 'Título A-Z' },
    { value: '-title', label: 'Título Z-A' },
    { value: 'due_date', label: 'Prazo (Crescente)' },
    { value: '-due_date', label: 'Prazo (Decrescente)' },
    { value: 'priority', label: 'Prioridade (Baixa → Alta)' },
    { value: '-priority', label: 'Prioridade (Alta → Baixa)' }
  ];

  const handleInputChange = (field, value) => {
    setLocalFilters({
      ...localFilters,
      [field]: value
    });
  };

  const handleSearch = () => {
    onFiltersChange(localFilters);
  };

  const handleClearAll = () => {
    const clearedFilters = {
      search: '',
      status: '',
      priority: '',
      ordering: '-created_at',
      due_date_from: '',
      due_date_to: '',
      overdue: false
    };
    setLocalFilters(clearedFilters);
    onClearFilters();
  };

  const handleOverdueToggle = () => {
    const newOverdueValue = !localFilters.overdue;
    const updatedFilters = {
      ...localFilters,
      overdue: newOverdueValue
    };
    setLocalFilters(updatedFilters);
    onFiltersChange(updatedFilters);
  };

  const hasActiveFilters = Object.values(localFilters).some(value => 
    value !== '' && value !== null && value !== undefined && value !== false
  );

  return (
    <div className="task-filters">
      <div className="filters-header">
        <div className="filters-title">
          <FiFilter className="filter-icon" />
          <h3>Filtros</h3>
        </div>
        {hasActiveFilters && (
          <button 
            onClick={handleClearAll}
            className="clear-filters-btn"
            disabled={loading}
          >
            <FiX />
            Limpar Filtros
          </button>
        )}
      </div>

      <div className="filters-grid">

        <div className="filter-group">
          <label htmlFor="search">Buscar por Título</label>
          <div className="search-input-container">
            <FiSearch className="search-icon" />
            <input
              id="search"
              type="text"
              placeholder="Digite o título da tarefa..."
              value={localFilters.search || ''}
              onChange={(e) => handleInputChange('search', e.target.value)}
              disabled={loading}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
          </div>
        </div>


        <div className="filter-group">
          <label htmlFor="status">Status</label>
          <select
            id="status"
            value={localFilters.status || ''}
            onChange={(e) => handleInputChange('status', e.target.value)}
            disabled={loading}
          >
            {statusOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>


        <div className="filter-group">
          <label htmlFor="priority">Prioridade</label>
          <select
            id="priority"
            value={localFilters.priority || ''}
            onChange={(e) => handleInputChange('priority', e.target.value)}
            disabled={loading}
          >
            {priorityOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="ordering">Ordenar por</label>
          <select
            id="ordering"
            value={localFilters.ordering || '-created_at'}
            onChange={(e) => handleInputChange('ordering', e.target.value)}
            disabled={loading}
          >
            {orderingOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>


        <div className="filter-group">
          <label htmlFor="due_date_from">Data de Vencimento (De)</label>
          <input
            id="due_date_from"
            type="date"
            value={localFilters.due_date_from || ''}
            onChange={(e) => handleInputChange('due_date_from', e.target.value)}
            disabled={loading}
          />
        </div>

        <div className="filter-group">
          <label htmlFor="due_date_to">Data de Vencimento (Até)</label>
          <input
            id="due_date_to"
            type="date"
            value={localFilters.due_date_to || ''}
            onChange={(e) => handleInputChange('due_date_to', e.target.value)}
            disabled={loading}
          />
        </div>

        <div className="filter-group filter-actions">
          <button
            onClick={handleOverdueToggle}
            className={`overdue-btn ${localFilters.overdue ? 'active' : ''}`}
            disabled={loading}
          >
            <FiClock />
            {localFilters.overdue ? 'Exibindo Atrasadas' : 'Mostrar Atrasadas'}
          </button>
          
          <button
            onClick={handleSearch}
            className="search-btn primary"
            disabled={loading}
          >
            <FiSearch />
            Buscar
          </button>
        </div>
      </div>
    </div>
  );
};

export default TaskFilters;
