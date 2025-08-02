import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { FiPlus, FiEdit, FiTrash2, FiCheck, FiX, FiClock, FiTag, FiSettings } from 'react-icons/fi';
import DataTable from '../../components/common/DataTable';
import TaskFilters from '../../components/common/TaskFilters';
import TaskModal from '../../components/common/TaskModal';
import ConfirmationModal from '../../components/common/ConfirmationModal';
import taskService from '../../services/taskService';
import './ToDoList.css';

function ToDoListPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [modalLoading, setModalLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const [confirmationModal, setConfirmationModal] = useState({
    isOpen: false,
    type: 'confirm',
    title: '',
    message: '',
    onConfirm: null
  });
  const [taskToDelete, setTaskToDelete] = useState(null);
  const [confirmationLoading, setConfirmationLoading] = useState(false);
  
  // Filtros que estão sendo editados (no componente de filtros)
  const [filters, setFilters] = useState({
    search: '',
    status: '',
    priority: '',
    ordering: '-created_at',
    due_date_from: '',
    due_date_to: '',
    overdue: false
  });
  
  // Filtros que estão atualmente aplicados (usados nas requisições)
  const [appliedFilters, setAppliedFilters] = useState({
    search: '',
    status: '',
    priority: '',
    ordering: '-created_at',
    due_date_from: '',
    due_date_to: '',
    overdue: false
  });

  const loadTasks = useCallback(async (page = currentPage, size = pageSize, currentFilters = appliedFilters) => {
    setLoading(true);
    try {
      const params = {
        page,
        page_size: size,
        ...currentFilters
      };
      Object.keys(params).forEach(key => {
        if (params[key] === '' || params[key] === null || params[key] === undefined) {
          delete params[key];
        }
      });

      const response = await taskService.getTasks(params);

      if (Array.isArray(response)) {
        setTasks(response);
        setTotalItems(response.length);
        setTotalPages(Math.ceil(response.length / size));
      } else {
        setTasks(response.results || []);
        setTotalItems(response.count || 0);
        setTotalPages(Math.ceil((response.count || 0) / size));
      }
    } catch (error) {
      console.error('Erro ao carregar tarefas:', error);
    } finally {
      setLoading(false);
    }
  }, [currentPage, pageSize, appliedFilters]);

  useEffect(() => {
    loadTasks();
  }, [loadTasks]);

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const showConfirmationModal = (type, title, message, onConfirm = null) => {
    setConfirmationModal({
      isOpen: true,
      type,
      title,
      message,
      onConfirm
    });
  };

  const closeConfirmationModal = () => {
    setConfirmationModal({
      isOpen: false,
      type: 'confirm',
      title: '',
      message: '',
      onConfirm: null
    });
    setTaskToDelete(null);
    setConfirmationLoading(false);
  };

  const handleCreateTask = () => {
    setEditingTask(null);
    setModalOpen(true);
  };

  const handleManageCategories = () => {
    navigate('/gerenciarCategorias');
  };

  const handleEditTask = (task) => {
    setEditingTask(task);
    setModalOpen(true);
  };

  const handleSaveTask = async (taskData) => {
    setModalLoading(true);
    try {
      if (editingTask) {
        await taskService.updateTask(editingTask.id, taskData);
        showConfirmationModal(
          'success',
          'Tarefa Atualizada!',
          'A tarefa foi atualizada com sucesso.'
        );
      } else {
        await taskService.createTask(taskData);
        showConfirmationModal(
          'success',
          'Tarefa Criada!',
          'A nova tarefa foi criada com sucesso.'
        );
      }
      setModalOpen(false);
      setEditingTask(null);
      loadTasks(1);
      setCurrentPage(1);
    } catch (error) {
      console.error('Erro ao salvar tarefa:', error);
      showConfirmationModal(
        'error',
        'Erro ao Salvar',
        editingTask 
          ? 'Ocorreu um erro ao atualizar a tarefa. Tente novamente.'
          : 'Ocorreu um erro ao criar a tarefa. Tente novamente.'
      );
    } finally {
      setModalLoading(false);
    }
  };

  const handleDeleteTask = (taskId, taskTitle) => {
    setTaskToDelete(taskId);
    showConfirmationModal(
      'confirm',
      'Confirmar Exclusão',
      `Tem certeza que deseja excluir a tarefa "${taskTitle}"? Esta ação não pode ser desfeita.`,
      () => confirmDeleteTask(taskId)
    );
  };

  const confirmDeleteTask = async (taskId) => {
    setConfirmationLoading(true);
    try {
      await taskService.deleteTask(taskId);
      closeConfirmationModal();
      showConfirmationModal(
        'success',
        'Tarefa Excluída!',
        'A tarefa foi excluída com sucesso.'
      );
      loadTasks();
    } catch (error) {
      console.error('Erro ao excluir tarefa:', error);
      closeConfirmationModal();
      showConfirmationModal(
        'error',
        'Erro ao Excluir',
        'Ocorreu um erro ao excluir a tarefa. Tente novamente.'
      );
    } finally {
      setConfirmationLoading(false);
    }
  };

  const handleToggleComplete = (task) => {
    if (task.is_completed) {
      showConfirmationModal(
        'confirm',
        'Reabrir Tarefa',
        `Tem certeza que deseja reabrir a tarefa "${task.title}" e marcá-la como não concluída?`,
        () => confirmToggleComplete(task)
      );
    } else {
      showConfirmationModal(
        'confirm',
        'Concluir Tarefa',
        `Tem certeza que deseja marcar a tarefa "${task.title}" como concluída?`,
        () => confirmToggleComplete(task)
      );
    }
  };

  const confirmToggleComplete = async (task) => {
    setConfirmationLoading(true);
    try {
      if (task.is_completed) {
        await taskService.markIncomplete(task.id);
        closeConfirmationModal();
        showConfirmationModal(
          'success',
          'Tarefa Reaberta!',
          'A tarefa foi marcada como não concluída com sucesso.'
        );
      } else {
        await taskService.markCompleted(task.id);
        closeConfirmationModal();
        showConfirmationModal(
          'success',
          'Tarefa Concluída!',
          'A tarefa foi marcada como concluída com sucesso.'
        );
      }
      loadTasks();
    } catch (error) {
      console.error('Erro ao atualizar status da tarefa:', error);
      closeConfirmationModal();
      showConfirmationModal(
        'error',
        'Erro ao Atualizar',
        'Ocorreu um erro ao atualizar o status da tarefa. Tente novamente.'
      );
    } finally {
      setConfirmationLoading(false);
    }
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
    loadTasks(page, pageSize, appliedFilters);
  };

  const handlePageSizeChange = (size) => {
    setPageSize(size);
    setCurrentPage(1);
    loadTasks(1, size, appliedFilters);
  };

  const handleFiltersChange = (newFilters) => {
    // Aplicar os novos filtros e resetar para a primeira página
    setFilters(newFilters);
    setAppliedFilters(newFilters);
    setCurrentPage(1);
    loadTasks(1, pageSize, newFilters);
  };

  const handleClearFilters = () => {
    const clearedFilters = {
      search: '',
      status: '',
      priority: '',
      ordering: '-created_at',
      due_date_from: '',
      due_date_to: '',
      overdue: false
    };
    setFilters(clearedFilters);
    setAppliedFilters(clearedFilters);
    setCurrentPage(1);
    loadTasks(1, pageSize, clearedFilters);
  };

  const formatDate = (dateString) => {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR');
  };

  const renderStatusBadge = (status) => {
    const statusMap = {
      pending: { label: 'Pendente', class: 'status-pending' },
      in_progress: { label: 'Em Progresso', class: 'status-in_progress' },
      completed: { label: 'Concluído', class: 'status-completed' },
      cancelled: { label: 'Cancelado', class: 'status-cancelled' }
    };
    const statusInfo = statusMap[status] || { label: status, class: '' };
    return (
      <span className={`status-badge ${statusInfo.class}`}>
        {statusInfo.label}
      </span>
    );
  };

  const renderPriorityBadge = (priority) => {
    const priorityMap = {
      low: { label: 'Baixa', class: 'priority-low' },
      medium: { label: 'Média', class: 'priority-medium' },
      high: { label: 'Alta', class: 'priority-high' },
      urgent: { label: 'Urgente', class: 'priority-urgent' }
    };
    const priorityInfo = priorityMap[priority] || { label: priority, class: '' };
    return (
      <span className={`priority-badge ${priorityInfo.class}`}>
        {priorityInfo.label}
      </span>
    );
  };

  const renderTags = (tagsString) => {
    if (!tagsString) return '-';
    const tags = tagsString.split(',').map(tag => tag.trim()).filter(tag => tag);
    return (
      <div className="tags-container">
        {tags.map((tag, index) => (
          <span key={index} className="tag">
            <FiTag size={12} />
            {tag}
          </span>
        ))}
      </div>
    );
  };

  const columns = [
    {
      header: 'Título',
      accessor: 'title',
      cell: (task) => (
        <div className="task-title-cell">
          <strong>{task.title}</strong>
          {task.description && (
            <div className="task-description">{task.description}</div>
          )}
        </div>
      )
    },
    {
      header: 'Status',
      accessor: 'status',
      cell: (task) => renderStatusBadge(task.status),
      className: 'text-center'
    },
    {
      header: 'Prioridade',
      accessor: 'priority',
      cell: (task) => renderPriorityBadge(task.priority),
      className: 'text-center'
    },
    {
      header: 'Vencimento',
      accessor: 'due_date',
      cell: (task) => (
        <div className={`due-date-cell ${task.is_overdue ? 'overdue' : ''}`}>
          {task.due_date ? (
            <>
              <FiClock size={12} />
              {formatDate(task.due_date)}
              {task.is_overdue && <span className="overdue-label">Atrasada</span>}
            </>
          ) : (
            '-'
          )}
        </div>
      )
    },
    {
      header: 'Tags',
      accessor: 'tags',
      cell: (task) => renderTags(task.tags)
    },
    {
      header: 'Ações',
      accessor: 'actions',
      cell: (task) => (
        <div className="action-buttons">
          <button
            onClick={() => handleToggleComplete(task)}
            className={`action-btn ${task.is_completed ? 'complete' : 'incomplete'}`}
            title={task.is_completed ? 'Marcar como não concluída' : 'Marcar como concluída'}
          >
            {task.is_completed ? <FiX /> : <FiCheck />}
          </button>
          <button
            onClick={() => handleEditTask(task)}
            className="action-btn edit"
            title="Editar tarefa"
          >
            <FiEdit />
          </button>
          <button
            onClick={() => handleDeleteTask(task.id, task.title)}
            className="action-btn delete"
            title="Excluir tarefa"
          >
            <FiTrash2 />
          </button>
        </div>
      ),
      className: 'text-center'
    }
  ];

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <div className="dashboard-header-content" style={{
          cursor: 'pointer',
        }}>
          <h1
            onClick={() => window.location.href = '/todolist'}
          >To-Do List</h1>
          <div className="user-info">
            <span>Olá, {user?.first_name || 'Usuário'}!</span>
            <button onClick={handleLogout} className="logout-button">
              Sair
            </button>
          </div>
        </div>
      </header>

      <main className="dashboard-main">
        <div className="create-task-section">
          <div className="section-header">
            <h2>Bem-vindo ao Sistema de Tarefas!</h2>
            <p>Gerencie suas tarefas de forma eficiente e organizada.</p>
          </div>

          <div className="create-task-card">
            <div className="action-buttons-container">
              <button
                onClick={handleCreateTask}
                className="create-task-btn primary"
              >
                <FiPlus />
                Nova Tarefa
              </button>

              <button
                onClick={handleManageCategories}
                className="create-task-btn secondary"
              >
                <FiSettings />
                Gerenciar Categorias
              </button>
            </div>
          </div>
        </div>
        <TaskFilters
          filters={filters}
          onFiltersChange={handleFiltersChange}
          onClearFilters={handleClearFilters}
          loading={loading}
        />
        <div className="tasks-section">
          <div className="section-title">
            <h3>Suas Tarefas</h3>
            <span className="tasks-count">
              {totalItems} {totalItems === 1 ? 'tarefa encontrada' : 'tarefas encontradas'}
            </span>
          </div>
          <DataTable
            data={tasks}
            columns={columns}
            pagination={true}
            pageSize={pageSize}
            currentPage={currentPage}
            totalPages={totalPages}
            totalItems={totalItems}
            onPageChange={handlePageChange}
            onPageSizeChange={handlePageSizeChange}
            loading={loading}
            emptyMessage="Nenhuma tarefa encontrada. Crie sua primeira tarefa!"
          />

        </div>
      </main>
      <TaskModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        onSave={handleSaveTask}
        task={editingTask}
        loading={modalLoading}
      />
      
      <ConfirmationModal
        isOpen={confirmationModal.isOpen}
        type={confirmationModal.type}
        title={confirmationModal.title}
        message={confirmationModal.message}
        onClose={closeConfirmationModal}
        onConfirm={confirmationModal.onConfirm}
        loading={confirmationLoading}
        confirmText={
          confirmationModal.type === 'confirm' 
            ? confirmationModal.title === 'Confirmar Exclusão' 
              ? 'Sim, Excluir'
              : confirmationModal.title === 'Concluir Tarefa'
                ? 'Sim, Concluir'
                : confirmationModal.title === 'Reabrir Tarefa'
                  ? 'Sim, Reabrir'
                  : 'Confirmar'
            : 'OK'
        }
        cancelText="Cancelar"
        showCancel={confirmationModal.type === 'confirm'}
      />
    </div>
  );
}

export default ToDoListPage;
