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
  }
};

export default taskService;
