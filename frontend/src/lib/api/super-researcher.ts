import { apiClient } from './client';
import { SuperResearcher, SuperResearcherFormData, SuperResearcherFilters } from '../types/super-researcher';

export const superResearcherApi = {
  // Get all super researchers with optional filtering
  getAllSuperResearchers: async (filters?: SuperResearcherFilters): Promise<SuperResearcher[]> => {
    const params: Record<string, string> = {};
    if (filters?.promoted !== undefined) params.promoted = String(filters.promoted);
    if (filters?.is_active_lead !== undefined) params.is_active_lead = String(filters.is_active_lead);
    if (filters?.lead_class) params.lead_class = filters.lead_class;

    return apiClient.get<SuperResearcher[]>('/api/super_researcher/', params);
  },

  // Get current lead
  getCurrentLead: async (): Promise<SuperResearcher> => {
    return apiClient.get<SuperResearcher>('/api/super_researcher/current-lead/');
  },

  // Get single super researcher by ID
  getSuperResearcherById: async (id: number): Promise<SuperResearcher> => {
    return apiClient.get<SuperResearcher>(`/api/super_researcher/${id}`);
  },

  // Generate leads using AI
  generateLeads: async (): Promise<SuperResearcher[]> => {
    return apiClient.get<SuperResearcher[]>('/api/super_researcher/generate-leads/');
  },

  // Create new super researcher
  createSuperResearcher: async (data: SuperResearcherFormData): Promise<SuperResearcher> => {
    return apiClient.post<SuperResearcher>('/api/super_researcher/', data);
  },

  // Update existing super researcher
  updateSuperResearcher: async (id: number, data: SuperResearcherFormData): Promise<SuperResearcher> => {
    return apiClient.put<SuperResearcher>(`/api/super_researcher/${id}`, data);
  },

  // Delete super researcher
  deleteSuperResearcher: async (id: number): Promise<{ success: boolean }> => {
    return apiClient.delete<{ success: boolean }>(`/api/super_researcher/${id}`);
  },

  // Toggle promoted status
  togglePromoted: async (id: number, promoted: boolean): Promise<SuperResearcher> => {
    return apiClient.put<SuperResearcher>(`/api/super_researcher/${id}`, { promoted });
  },

  // Toggle active lead status
  toggleActiveLead: async (id: number, is_active_lead: boolean): Promise<SuperResearcher> => {
    return apiClient.put<SuperResearcher>(`/api/super_researcher/${id}`, { is_active_lead });
  },

  // Update lead class
  updateLeadClass: async (id: number, lead_class: string): Promise<SuperResearcher> => {
    return apiClient.put<SuperResearcher>(`/api/super_researcher/${id}`, { lead_class });
  },

  // Update notes
  updateNotes: async (id: number, notes: string): Promise<SuperResearcher> => {
    return apiClient.put<SuperResearcher>(`/api/super_researcher/${id}`, { notes });
  }
};