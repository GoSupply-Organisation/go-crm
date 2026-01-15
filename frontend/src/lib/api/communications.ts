import { apiClient } from './client';

export interface EmailData {
  subject: string;
  message: string;
}

export interface SMSData {
  message: string;
}

export const communicationsApi = {
  sendEmail: async (contactId: number, data: EmailData): Promise<{ success: boolean; message: string }> => {
    return apiClient.post<{ success: boolean; message: string }>(`/api/communications/send-email/${contactId}`, data);
  },

  sendSMS: async (contactId: number, data: SMSData): Promise<{ success: boolean; message: string }> => {
    return apiClient.post<{ success: boolean; message: string }>(`/api/communications/send-sms/${contactId}`, data);
  },
};