import { useState, useEffect, useCallback } from 'react';
import { superResearcherApi } from '../api/super-researcher';
import { SuperResearcher, SuperResearcherFormData, SuperResearcherFilters } from '../types/super-researcher';
import { ApiError } from '../api/client';

export function useSuperResearchers(filters?: SuperResearcherFilters) {
  const [researchers, setResearchers] = useState<SuperResearcher[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchResearchers = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await superResearcherApi.getAllSuperResearchers(filters);
      setResearchers(data);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('Failed to fetch researchers');
      }
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchResearchers();
  }, [fetchResearchers]);

  return { researchers, loading, error, refetch: fetchResearchers };
}

export function useSuperResearcher(id: number) {
  const [researcher, setResearcher] = useState<SuperResearcher | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchResearcher() {
      if (!id) return;
      setLoading(true);
      setError(null);
      try {
        const data = await superResearcherApi.getSuperResearcherById(id);
        setResearcher(data);
      } catch (err) {
        if (err instanceof ApiError) {
          setError(err.message);
        } else {
          setError('Failed to fetch researcher');
        }
      } finally {
        setLoading(false);
      }
    }

    fetchResearcher();
  }, [id]);

  return { researcher, loading, error };
}

export function useCurrentLead() {
  const [currentLead, setCurrentLead] = useState<SuperResearcher | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchCurrentLead = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await superResearcherApi.getCurrentLead();
      setCurrentLead(data);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('Failed to fetch current lead');
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCurrentLead();
  }, [fetchCurrentLead]);

  return { currentLead, loading, error, refetch: fetchCurrentLead };
}

export function useSuperResearcherOperations() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createResearcher = useCallback(async (data: SuperResearcherFormData) => {
    setLoading(true);
    setError(null);
    try {
      const result = await superResearcherApi.createSuperResearcher(data);
      return result;
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('Failed to create researcher');
      }
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const updateResearcher = useCallback(async (id: number, data: SuperResearcherFormData) => {
    setLoading(true);
    setError(null);
    try {
      const result = await superResearcherApi.updateSuperResearcher(id, data);
      return result;
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('Failed to update researcher');
      }
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const deleteResearcher = useCallback(async (id: number) => {
    setLoading(true);
    setError(null);
    try {
      const result = await superResearcherApi.deleteSuperResearcher(id);
      return result;
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('Failed to delete researcher');
      }
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const generateLeads = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await superResearcherApi.generateLeads();
      return result;
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('Failed to generate leads');
      }
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const togglePromoted = useCallback(async (id: number, promoted: boolean) => {
    setLoading(true);
    setError(null);
    try {
      const result = await superResearcherApi.togglePromoted(id, promoted);
      return result;
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('Failed to toggle promoted status');
      }
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const toggleActiveLead = useCallback(async (id: number, is_active_lead: boolean) => {
    setLoading(true);
    setError(null);
    try {
      const result = await superResearcherApi.toggleActiveLead(id, is_active_lead);
      return result;
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('Failed to toggle active lead status');
      }
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const updateLeadClass = useCallback(async (id: number, lead_class: string) => {
    setLoading(true);
    setError(null);
    try {
      const result = await superResearcherApi.updateLeadClass(id, lead_class);
      return result;
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('Failed to update lead class');
      }
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const updateNotes = useCallback(async (id: number, notes: string) => {
    setLoading(true);
    setError(null);
    try {
      const result = await superResearcherApi.updateNotes(id, notes);
      return result;
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('Failed to update notes');
      }
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    createResearcher,
    updateResearcher,
    deleteResearcher,
    generateLeads,
    togglePromoted,
    toggleActiveLead,
    updateLeadClass,
    updateNotes,
    loading,
    error,
  };
}