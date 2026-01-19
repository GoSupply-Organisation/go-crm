import { LeadClassification } from './contact';

export interface SuperResearcher {
  id: number;
  company: string;
  website: string;
  full_name: string;
  email: string;
  phone_number: string;
  promoted: boolean;
  is_active_lead: boolean;
  lead_class: LeadClassification;
  notes: string;
  address: string;
}

export interface SuperResearcherFormData {
  company: string;
  website?: string;
  full_name: string;
  email: string;
  phone_number?: string;
  lead_class?: LeadClassification;
  notes?: string;
  address?: string;
}

export interface SuperResearcherFilters {
  promoted?: boolean;
  is_active_lead?: boolean;
  lead_class?: LeadClassification;
}