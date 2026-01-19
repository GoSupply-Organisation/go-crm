import { CommunicationLog } from "./communications";

export type LeadClassification =
  | 'New'
  | 'Contacted'
  | 'Growing Interest'
  | 'Leading'
  | 'Dying'
  | 'Converted'
  | 'Cold';

export interface Contact {
  id: number;
  Full_name: string;
  email: string;
  phone_number: string;
  company: string;
  lead_class: LeadClassification;
  notes: string;
  address: string;
  created_at: string;
}

export interface ContactFormData {
  Full_name: string;
  email: string;
  phone_number?: string;
  company?: string;
  lead_class?: LeadClassification;
  notes?: string;
  address?: string;
}

export interface ContactFilters {
  lead_class?: LeadClassification;
  search?: string;
  sort_by?: string;
}

export interface SentEmail {
  id: number;
  contact: number;
  subject: string;
  message: string;
  sent_at: string;
  from_email?: string;
  sent_by?: number;
}

export interface SentSms {
  id: number;
  contact: number;
  body: string;
  sent_at: string;
}

export interface EmailFormData {
  subject: string;
  message: string;
  from_email?: string;
}

export interface SmsFormData {
  body: string;
}


export interface CommunicationLogs {
  emails: CommunicationLog[];
  sms: CommunicationLog[];
}


export interface EditContactFormData {
  Full_name: string;
  email: string;
  phone_number: string;
  company: string;
  lead_class: LeadClassification;
  notes: string;
  address: string;
}

export interface EditContactFormProps {
  contact: Contact;
  onSubmit: (data: EditContactFormData) => Promise<void>;
  onCancel?: () => void;
}