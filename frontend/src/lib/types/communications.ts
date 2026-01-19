export interface CommunicationLog {
  id: number;
  contact: string;
  contact_id: number;
  subject?: string;
  message?: string;
  body?: string;
  sent_at: string;
}


export interface EmailData {
  subject: string;
  message: string;
}

export interface SMSData {
  message: string;
}

