// In process of migrating this. 
import { apiClient } from './client';
import { Todo, TodoFormData, TodoFilters } from '../types/todos';

export const todosApi = {
  // Get all todos with optional filters
  getAllTodos: async (filters?: TodoFilters): Promise<Todo[]> => {
    const params: Record<string, string> = {};
    if (filters?.completed !== undefined) params.completed = String(filters.completed);
    if (filters?.priority) params.priority = filters.priority;

    return apiClient.get<Todo[]>('/api/todos/', params);
  },

  // Get single todo by ID
  getTodoById: async (id: number): Promise<Todo> => {
    return apiClient.get<Todo>(`/api/todos/${id}`);
  },

  // Create new todo
  createTodo: async (data: TodoFormData): Promise<Todo> => {
    return apiClient.post<Todo>('/api/todos/', data);
  },

  // Update existing todo
  updateTodo: async (id: number, data: TodoFormData): Promise<Todo> => {
    return apiClient.put<Todo>(`/api/todos/${id}`, data);
  },

  // Delete todo
  deleteTodo: async (id: number): Promise<{ success: boolean }> => {
    return apiClient.delete<{ success: boolean }>(`/api/todos/${id}`);
  },
};