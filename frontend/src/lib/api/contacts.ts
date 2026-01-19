import { apiClient } from './client';
import {
  Contact,
  ContactFormData,
  ContactFilters,
  SentEmail,
  SentSms,
  EmailFormData,
  SmsFormData,
  EditContactFormData,
} from '../types/contact';
import { MoreInfoResponse } from '../types/moreinfo';
import { CommunicationLogs } from '../types/contact';


export const contactsApi = {
  // Get all contacts with optional filters
  getAllContacts: async (filters?: ContactFilters): Promise<Contact[]> => {
    const params: Record<string, string> = {};
    if (filters?.lead_class) params.lead_class = filters.lead_class;
    if (filters?.search) params.search = filters.search;
    if (filters?.sort_by) params.sort_by = filters.sort_by;

    return apiClient.get<Contact[]>('/api/contact/index', params);
  },

  // Get single contact by ID
  getContactById: async (contact_id: number): Promise<Contact> => {
    return apiClient.get<Contact>(`/api/contact/moreinfo/${contact_id}`);
  },

  // Create new contact
  createContact: async (data: ContactFormData): Promise<Contact> => {
    return apiClient.post<Contact>('/api/contact/add', data);
  },

  // Update existing contact
  updateContact: async (contact_id: number, data: ContactFormData): Promise<Contact> => {
    return apiClient.put<Contact>(`/api/contact/update/${contact_id}`, data);
  },

  // Delete contact
  deleteContact: async (contact_id: number): Promise<{ success: boolean; message: string }> => {
    return apiClient.delete<{ success: boolean; message: string }>(`/api/contact/delete/${contact_id}`);
  },

  // Send email to contact
  sendEmail: async (contact_id: number, data: EmailFormData): Promise<SentEmail> => {
    return apiClient.post<SentEmail>(`/api/contact/send-email/${contact_id}`, data);
  },

  // Send SMS to contact
  sendSms: async (contact_id: number, data: SmsFormData): Promise<SentSms> => {
    return apiClient.post<SentSms>(`/api/contact/send-sms/${contact_id}`, data);
  },

  // Get contact's email history
  getContactEmails: async (contact_id: number): Promise<SentEmail[]> => {
    return apiClient.get<SentEmail[]>(`/api/contact/contact-emails/${contact_id}`);
  },

  editContact: async (contactId: number, data: EditContactFormData) => {
    return apiClient.put(`/api/contact/update/${contactId}`, data);
  },

  getMoreInfoById: async (contact_id: number): Promise<MoreInfoResponse> => {
        const params: Record<string, string> = {};
        return apiClient.get<MoreInfoResponse>(`/api/contact/moreinfo/${contact_id}`, params);
    },

  getCommunicationLogs: async (): Promise<CommunicationLogs[]> => {
    return apiClient.get<CommunicationLogs[]>('/api/contact/communication-logs');
}

};
