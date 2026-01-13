// These have not use been written at least on the backend when backend is more stable then these will be implemented

import { apiClient } from './client';
import { ApexContact, ApexFormData, ApexFilters } from '../types/apex';

export const apexApi = {
  // Get all apex research contacts
  getAllApexContacts: async (filters?: ApexFilters): Promise<ApexContact[]> => {
    const params: Record<string, string> = {};
    if (filters?.promoted !== undefined) params.promoted = String(filters.promoted);
    if (filters?.is_active_lead !== undefined) params.is_active_lead = String(filters.is_active_lead);
    if (filters?.lead_class) params.lead_class = filters.lead_class;

    return apiClient.get<ApexContact[]>('/api/apex/contacts', params);
  },

  // Get single apex contact by ID
  getApexContactById: async (id: number): Promise<ApexContact> => {
    return apiClient.get<ApexContact>(`/api/apex/${id}`);
  },

  // Create new apex contact
  createApexContact: async (data: ApexFormData): Promise<ApexContact> => {
    return apiClient.post<ApexContact>('/api/apex/contacts', data);
  },

  // Update existing apex contact
  updateApexContact: async (id: number, data: ApexFormData): Promise<ApexContact> => {
    return apiClient.put<ApexContact>(`/api/apex/${id}`, data);
  },

  // Delete apex contact
  deleteApexContact: async (id: number): Promise<{ success: boolean }> => {
    return apiClient.delete<{ success: boolean }>(`/api/apex/${id}`);
  },

  // Promote apex contact to staged lead
  promoteApexContact: async (id: number): Promise<{ success: boolean; message: string }> => {
    return apiClient.post<{ success: boolean; message: string }>(`/api/apex/contacts/${id}/promote`, {});
  },

  // Get apex research data/tenders
  getApexHome: async (): Promise<any> => {
    return apiClient.get('/api/apex/home');
  },
};