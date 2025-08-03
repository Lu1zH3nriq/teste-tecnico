import api from './api';

const taskService = {
  // Listar todas as tarefas com filtros
  getTasks: async (params = {}) => {
    try {
      const response = await api.get('/api/tasks/', { params });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Criar nova tarefa
  createTask: async (taskData) => {
    try {
      const response = await api.post('/api/tasks/', taskData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Atualizar tarefa
  updateTask: async (taskId, taskData) => {
    try {
      const response = await api.put(`/api/tasks/${taskId}/`, taskData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Deletar tarefa
  deleteTask: async (taskId) => {
    try {
      await api.delete(`/api/tasks/${taskId}/`);
      return true;
    } catch (error) {
      throw error;
    }
  },

  // Obter tarefa por ID
  getTask: async (taskId) => {
    try {
      const response = await api.get(`/api/tasks/${taskId}/`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Marcar tarefa como concluída
  markCompleted: async (taskId) => {
    try {
      const response = await api.patch(`/api/tasks/${taskId}/toggle/`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Marcar tarefa como não concluída
  markIncomplete: async (taskId) => {
    try {
      const response = await api.patch(`/api/tasks/${taskId}/toggle/`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Obter usuários compartilhados de uma tarefa
  getSharedUsers: async (taskId) => {
    try {
      const response = await api.get(`/api/tasks/${taskId}/shared-users/`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Compartilhar tarefa com usuário
  shareTaskWithUser: async (taskId, email) => {
    try {
      const response = await api.post(`/api/tasks/${taskId}/shared-users/`, {
        email: email
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Remover usuário do compartilhamento
  removeUserFromTask: async (taskId, userId) => {
    try {
      const response = await api.post(`/api/tasks/${taskId}/remove-user/`, {
        user_id: userId
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  }
};

export default taskService;
