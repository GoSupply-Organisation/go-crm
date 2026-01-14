// In process of migrating this. 
import { apiClient } from './client';
import { Todo, TodoFormData, TodoFilters } from '../types/todos';

export const todosApi = {
  // Get all todos
  getAllTodos: async (filters?: TodoFilters): Promise<Todo[]> => {
    return apiClient.get<Todo[]>('/api/todo/index');
  },

  // Get todo statistics
  getStats: async (): Promise<{
    total: number;
    pending: number;
    completed: number;
  }> => {
    return apiClient.get('/api/todo/stats');
  },

  // Get single todo by ID
  getTodoById: async (todo_id: number): Promise<Todo> => {
    return apiClient.get<Todo>(`/api/todo/moreinfo/${todo_id}`);
  },

  // Create new todo
  createTodo: async (data: TodoFormData): Promise<Todo> => {
    return apiClient.post<Todo>('/api/todo/add', data);
  },

  // Update existing todo
  updateTodo: async (todo_id: number, data: TodoFormData): Promise<Todo> => {
    return apiClient.post<Todo>(`/api/todo/update/${todo_id}`, data);
  },

  // Delete todo
  deleteTodo: async (todo_id: number): Promise<{ success: boolean; message: string }> => {
    return apiClient.delete<{ success: boolean; message: string }>(`/api/todo/delete/${todo_id}`);
  },

  // Toggle todo completion status
  toggleTodo: async (todo_id: number): Promise<Todo> => {
    return apiClient.post<Todo>(`/api/todo/toggle/${todo_id}`, {});
  },
};