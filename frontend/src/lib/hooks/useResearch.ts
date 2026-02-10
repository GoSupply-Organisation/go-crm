import { useState, useEffect, useCallback } from 'react';
import { apexApi } from '../api/apex';
import { superResearcherApi } from '../api/super-researcher';
import { ApexContact, ApexFilters } from '../types/apex';
import { SuperResearcher, SuperResearcherFilters } from '../types/super-researcher';
import { ApiError } from '../api/client';

export function useApexResearch(filters?: ApexFilters) {
  const [apexContacts, setApexContacts] = useState<ApexContact[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchApexContacts = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apexApi.getAllApexContacts(filters);
      setApexContacts(data);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('Failed to fetch apex contacts');
      }
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchApexContacts();
  }, [fetchApexContacts]);

  return { apexContacts, loading, error, refetch: fetchApexContacts };
}

export function useSuperResearcher(filters?: SuperResearcherFilters) {
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

export function useResearchPipeline() {
  const [stagedLeads, setStagedLeads] = useState<{
    apex: ApexContact[];
    super: SuperResearcher[];
  }>({ apex: [], super: [] });
  const [activeLeads, setActiveLeads] = useState<{
    apex: ApexContact[];
    super: SuperResearcher[];
  }>({ apex: [], super: [] });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPipelineData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [apexPromoted, superPromoted, apexActive, superActive] = await Promise.all([
        apexApi.getAllApexContacts({ promoted: true }),
        superResearcherApi.getAllSuperResearchers({ promoted: true }),
        apexApi.getAllApexContacts({ is_active_lead: true }),
        superResearcherApi.getAllSuperResearchers({ is_active_lead: true }),
      ]);

      setStagedLeads({ apex: apexPromoted, super: superPromoted });
      setActiveLeads({ apex: apexActive, super: superActive });
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('Failed to fetch pipeline data');
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPipelineData();
  }, [fetchPipelineData]);

  const promoteApexContact = useCallback(async (id: number) => {
    try {
      await apexApi.promoteApexContact(id);
      await fetchPipelineData();
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      }
      throw err;
    }
  }, [fetchPipelineData]);

  return {
    stagedLeads,
    activeLeads,
    loading,
    error,
    refetch: fetchPipelineData,
    promoteApexContact,
  };
}