import { apiClient } from './client';
import { SuperResearcher, SuperResearcherUpdate, SuperResearcherFilters } from '../types/super-researcher';

export const superResearcherApi = {
  // Get all super researchers with optional filtering
  getAllSuperResearchers: async (filters?: SuperResearcherFilters): Promise<SuperResearcher[]> => {
    const params: Record<string, string> = {};
    if (filters?.promoted !== undefined) params.promoted = String(filters.promoted);
    if (filters?.is_active_lead !== undefined) params.is_active_lead = String(filters.is_active_lead);
    if (filters?.lead_class) params.lead_class = filters.lead_class;

    return apiClient.get<SuperResearcher[]>('/api/super_researcher/', params);
  },

  getCurrentLeads: async (): Promise<SuperResearcher> => {
    return apiClient.get<SuperResearcher>('/api/super_researcher/current-leads/');
  },
  
  GenerateLeads: async (): Promise<SuperResearcher[]> => {
    return apiClient.get<SuperResearcher[]>('/api/super_researcher/generate-leads/');
  },

  UpdateLeads: async (id: number, data: SuperResearcherUpdate): Promise<SuperResearcher> => {
    return apiClient.put<SuperResearcher>(`/api/super_researcher/${id}/`, data);
  },

  DeleteLeads: async (id: number): Promise<void> => {
    return apiClient.delete<void>(`/api/super_researcher/${id}/`);
  },
};