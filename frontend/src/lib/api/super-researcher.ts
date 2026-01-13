// These have not use been written at least on the backend when backend is more stable then these will be implemented

import { apiClient } from './client';
import { SuperResearcher, SuperResearcherFormData, SuperResearcherFilters } from '../types/super-researcher';

export const superResearcherApi = {
  // Get all super researchers
  getAllSuperResearchers: async (filters?: SuperResearcherFilters): Promise<SuperResearcher[]> => {
    const params: Record<string, string> = {};
    if (filters?.promoted !== undefined) params.promoted = String(filters.promoted);
    if (filters?.is_active_lead !== undefined) params.is_active_lead = String(filters.is_active_lead);
    if (filters?.lead_class) params.lead_class = filters.lead_class;

    return apiClient.get<SuperResearcher[]>('/api/super-researcher/', params);
  },

  // Get single super researcher by ID
  getSuperResearcherById: async (id: number): Promise<SuperResearcher> => {
    return apiClient.get<SuperResearcher>(`/api/super-researcher/${id}`);
  },

  // Create new super researcher
  createSuperResearcher: async (data: SuperResearcherFormData): Promise<SuperResearcher> => {
    return apiClient.post<SuperResearcher>('/api/super-researcher/', data);
  },

  // Update existing super researcher
  updateSuperResearcher: async (id: number, data: SuperResearcherFormData): Promise<SuperResearcher> => {
    return apiClient.put<SuperResearcher>(`/api/super-researcher/${id}`, data);
  },

  // Delete super researcher
  deleteSuperResearcher: async (id: number): Promise<{ success: boolean }> => {
    return apiClient.delete<{ success: boolean }>(`/api/super-researcher/${id}`);
  },
};