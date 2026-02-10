import { apiClient } from './client';
import { SuperResearcher, SuperResearcherUpdate, SuperResearcherFilters } from '../types/super-researcher';
import { LeadClassification } from '../types/contact';

export const superResearcherApi = {
  // Get all super researchers with optional filtering
  getAllSuperResearchers: async (filters?: SuperResearcherFilters): Promise<SuperResearcher[]> => {
    const params: Record<string, string> = {};
    if (filters?.promoted !== undefined) params.promoted = String(filters.promoted);
    if (filters?.is_active_lead !== undefined) params.is_active_lead = String(filters.is_active_lead);
    if (filters?.lead_class) params.lead_class = filters.lead_class;

    return apiClient.get<SuperResearcher[]>('/api/super_researcher/', params);
  },

  getSuperResearcherById: async (id: number): Promise<SuperResearcher> => {
    return apiClient.get<SuperResearcher>(`/api/super_researcher/${id}/`);
  },

  getCurrentLeads: async (): Promise<SuperResearcher> => {
    return apiClient.get<SuperResearcher>('/api/super_researcher/current-leads/');
  },

  GenerateLeads: async (): Promise<SuperResearcher[]> => {
    return apiClient.get<SuperResearcher[]>('/api/super_researcher/generate-leads/');
  },

  createSuperResearcher: async (data: SuperResearcherUpdate): Promise<SuperResearcher> => {
    return apiClient.post<SuperResearcher>('/api/super_researcher/', data);
  },

  updateSuperResearcher: async (id: number, data: SuperResearcherUpdate): Promise<SuperResearcher> => {
    return apiClient.put<SuperResearcher>(`/api/super_researcher/${id}/`, data);
  },

  deleteSuperResearcher: async (id: number): Promise<void> => {
    return apiClient.delete<void>(`/api/super_researcher/${id}/`);
  },

  togglePromoted: async (id: number, promoted: boolean): Promise<SuperResearcher> => {
    return superResearcherApi.updateSuperResearcher(id, { promoted });
  },

  toggleActiveLead: async (id: number, is_active_lead: boolean): Promise<SuperResearcher> => {
    return superResearcherApi.updateSuperResearcher(id, { is_active_lead });
  },

  updateLeadClass: async (id: number, lead_class: LeadClassification): Promise<SuperResearcher> => {
    return superResearcherApi.updateSuperResearcher(id, { lead_class });
  },

  updateNotes: async (id: number, notes: string): Promise<SuperResearcher> => {
    return superResearcherApi.updateSuperResearcher(id, { notes });
  },
};