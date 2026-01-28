import { LeadClassification } from './contact';

export interface SuperResearcher {
  id: number;
  company: string;
  website: string;
  full_name: string;
  phone_number: string;
  email: string;
  promoted: boolean;
  is_active_lead: boolean;
  lead_class: LeadClassification;
  notes: string;
  address: string;
}

export interface SuperResearcherUpdate {
  comapny?: string;
  website?: string;
  full_name?: string;
  phone_number?: string;
  email?: string;
  promoted?: boolean;
  is_active_lead?: boolean;
  lead_class?: LeadClassification;
  notes?: string;
  address?: string;
}
  


export interface SuperResearcherFilters {
  promoted?: boolean;
  is_active_lead?: boolean;
  lead_class?: LeadClassification;
}