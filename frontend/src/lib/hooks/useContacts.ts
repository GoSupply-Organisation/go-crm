import { useState, useEffect, useCallback, use } from 'react';
import { contactsApi } from '../api/contacts';
import { Contact, ContactFormData, ContactFilters, EditContactFormData } from '../types/contact';
import { ApiError } from '../api/client';

export function useContacts(filters?: ContactFilters) {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchContacts = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await contactsApi.getAllContacts(filters);
      setContacts(data);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('Failed to fetch contacts');
      }
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchContacts();
  }, [fetchContacts]);

  return { contacts, loading, error, refetch: fetchContacts };
}

export function useContact(id: number) {
  const [contact, setContact] = useState<Contact | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchContact() {
      if (!id) return;
      setLoading(true);
      setError(null);
      try {
        const data = await contactsApi.getContactById(id);
        setContact(data);
      } catch (err) {
        if (err instanceof ApiError) {
          setError(err.message);
        } else {
          setError('Failed to fetch contact');
        }
      } finally {
        setLoading(false);
      }
    }

    fetchContact();
  }, [id]);

  return { contact, loading, error };
}

export function useContactOperations() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createContact = useCallback(async (data: ContactFormData) => {
    setLoading(true);
    setError(null);
    try {
      const result = await contactsApi.createContact(data);
      return result;
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('Failed to create contact');
      }
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const updateContact = useCallback(async (id: number, data: ContactFormData) => {
    setLoading(true);
    setError(null);
    try {
      const result = await contactsApi.updateContact(id, data);
      return result;
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('Failed to update contact');
      }
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const deleteContact = useCallback(async (id: number) => {
    setLoading(true);
    setError(null);
    try {
      const result = await contactsApi.deleteContact(id);
      return result;
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('Failed to delete contact');
      }
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const sendEmail = useCallback(async (id: number, data: { subject: string; message: string; from_email?: string }) => {
    setLoading(true);
    setError(null);
    try {
      const result = await contactsApi.sendEmail(id, data);
      return result;
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('Failed to send email');
      }
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const sendSms = useCallback(async (id: number, data: { body: string }) => {
    setLoading(true);
    setError(null);
    try {
      const result = await contactsApi.sendSms(id, data);
      return result;
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('Failed to send SMS');
      }
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const editContact = useCallback(async (id: number, data: EditContactFormData) => {
    setLoading(true);
    setError(null);
    try {
      const result = await contactsApi.editContact(id, data);
      return result;
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('Failed to edit contact');
      }
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const getmoreinfo = useCallback(async (id: number) => {
    setLoading(true);
    setError(null);
    try {
      const result = await contactsApi.getContactById(id);
      return result;
    }
    catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      }
      else {
        setError('Failed to get more info');
      }
      throw err;
    }
    finally {
      setLoading(false);
    }
  }, []);

  const communicationlogs = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await contactsApi.getCommunicationLogs();
      return result;
    }
    catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      }
      else {
        setError('Failed to get communication logs');
      }
      throw err;
    }
    finally {
      setLoading(false);
    }
  }, []);


  return {
    createContact,
    updateContact,
    deleteContact,
    sendEmail,
    sendSms,
    editContact,
    getmoreinfo,
    communicationlogs,
    loading,
    error,
  };
}