'use client';

import React, { useState } from 'react';
import { MainLayout } from '@/components/layout/MainLayout';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Input } from '@/components/ui/Input';
import { SuperResearcher, SuperResearcherFilters } from '@/lib/types/super-researcher';
import { useSuperResearchers, useSuperResearcherOperations } from '@/lib/hooks/useSuperResearcher';
import { LeadClassification } from '@/lib/types/contact';
import { Loader } from '@/components/ui/Loader';
import { useRouter } from 'next/navigation';

const leadClassColors: Record<string, 'gray' | 'blue' | 'yellow' | 'orange' | 'purple' | 'green' | 'red'> = {
  'New': 'blue',
  'Contacted': 'yellow',
  'Growing Interest': 'orange',
  'Leading': 'purple',
  'Converted': 'green',
  'Cold': 'gray',
  'Dying': 'red'
};

export default function SuperResearcherPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterPromoted, setFilterPromoted] = useState<string>('all');
  const [filterActive, setFilterActive] = useState<string>('all');
  const [filterClass, setFilterClass] = useState<string>('all');
  const [showAddModal, setShowAddModal] = useState(false);
  const [showGenerateLoading, setShowGenerateLoading] = useState(false);

  const router = useRouter();

  // Build filters object
  const apiFilters: SuperResearcherFilters = {};
  if (filterPromoted === 'promoted') apiFilters.promoted = true;
  if (filterPromoted === 'not-promoted') apiFilters.promoted = false;
  if (filterActive === 'active') apiFilters.is_active_lead = true;
  if (filterActive === 'inactive') apiFilters.is_active_lead = false;
  if (filterClass !== 'all') apiFilters.lead_class = filterClass as LeadClassification;

  const { researchers, loading, error, refetch } = useSuperResearchers(apiFilters);
  const { generateLeads, deleteResearcher, togglePromoted, toggleActiveLead, updateLeadClass } = useSuperResearcherOperations();

  // Filter by search term
  const filteredResearchers = researchers.filter(researcher => {
    const matchesSearch =
      researcher.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      researcher.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      researcher.company?.toLowerCase().includes(searchTerm.toLowerCase());

    return matchesSearch;
  });

  const promotedCount = researchers.filter(r => r.promoted).length;
  const activeLeadsCount = researchers.filter(r => r.is_active_lead).length;
  const convertedCount = researchers.filter(r => r.lead_class === 'Converted').length;

  const handleGenerateLeads = async () => {
    try {
      setShowGenerateLoading(true);
      await generateLeads();
      await refetch();
      setShowGenerateLoading(false);
    } catch (error) {
      console.error('Failed to generate leads:', error);
      setShowGenerateLoading(false);
    }
  };

  const handleViewDetails = (id: number) => {
    router.push(`/super-researcher/${id}`);
  };

  const handleDelete = async (id: number) => {
    if (confirm('Are you sure you want to delete this researcher?')) {
      try {
        await deleteResearcher(id);
        await refetch();
      } catch (error) {
        console.error('Failed to delete researcher:', error);
      }
    }
  };

  const handleTogglePromoted = async (id: number, currentPromoted: boolean) => {
    try {
      await togglePromoted(id, !currentPromoted);
      await refetch();
    } catch (error) {
      console.error('Failed to toggle promoted status:', error);
    }
  };

  const handleToggleActiveLead = async (id: number, currentActive: boolean) => {
    try {
      await toggleActiveLead(id, !currentActive);
      await refetch();
    } catch (error) {
      console.error('Failed to toggle active lead status:', error);
    }
  };

  if (loading && researchers.length === 0) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center h-96">
          <Loader size="lg" />
        </div>
      </MainLayout>
    );
  }

  if (error && researchers.length === 0) {
    return (
      <MainLayout>
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Super Researcher</h1>
            <p className="text-gray-600 mt-1">
              Advanced research insights and lead intelligence
            </p>
          </div>
          <div className="flex gap-2">
            <Button
              variant="secondary"
              onClick={handleGenerateLeads}
              disabled={showGenerateLoading}
            >
              {showGenerateLoading ? <Loader size="sm" /> : 'Generate AI Leads'}
            </Button>
            <Button onClick={() => setShowAddModal(true)}>Add Research Target</Button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card title="Promoted Targets">
            <div className="text-3xl font-bold text-purple-600">{promotedCount}</div>
            <div className="text-sm text-gray-600">High priority research targets</div>
          </Card>
          <Card title="Active Leads">
            <div className="text-3xl font-bold text-blue-600">{activeLeadsCount}</div>
            <div className="text-sm text-gray-600">Currently engaging leads</div>
          </Card>
          <Card title="Converted">
            <div className="text-3xl font-bold text-green-600">{convertedCount}</div>
            <div className="text-sm text-gray-600">Successfully converted</div>
          </Card>
        </div>

        {/* Filters */}
        <Card title="Filter Results">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Input
              placeholder="Search researchers..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <select
              value={filterPromoted}
              onChange={(e) => setFilterPromoted(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Promotion Status</option>
              <option value="promoted">Promoted</option>
              <option value="not-promoted">Not Promoted</option>
            </select>
            <select
              value={filterActive}
              onChange={(e) => setFilterActive(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Active Status</option>
              <option value="active">Active Leads</option>
              <option value="inactive">Inactive Leads</option>
            </select>
            <select
              value={filterClass}
              onChange={(e) => setFilterClass(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Lead Classes</option>
              <option value="New">New</option>
              <option value="Contacted">Contacted</option>
              <option value="Growing Interest">Growing Interest</option>
              <option value="Leading">Leading</option>
              <option value="Converted">Converted</option>
              <option value="Cold">Cold</option>
              <option value="Dying">Dying</option>
            </select>
          </div>
        </Card>

        {/* Researchers List */}
        <div className="space-y-4">
          {filteredResearchers.map((researcher) => (
            <Card key={researcher.id}>
              <div className="space-y-4">
                {/* Header */}
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="font-semibold text-lg text-gray-900">{researcher.full_name}</h3>
                      {researcher.promoted && (
                        <Badge variant="purple">Promoted</Badge>
                      )}
                      <Badge variant={leadClassColors[researcher.lead_class]}>
                        {researcher.lead_class}
                      </Badge>
                      {researcher.is_active_lead && (
                        <Badge variant="blue">Active Lead</Badge>
                      )}
                    </div>
                    <div className="space-y-1">
                      <p className="text-sm text-gray-700">
                        <span className="font-medium">Company:</span> {researcher.company}
                      </p>
                      {researcher.website && (
                        <p className="text-sm text-gray-600">
                          <span className="font-medium">Website:</span>{' '}
                          <a
                            href={researcher.website}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:underline"
                          >
                            {researcher.website}
                          </a>
                        </p>
                      )}
                      <p className="text-sm text-gray-600">
                        <span className="font-medium">Email:</span> {researcher.email}
                      </p>
                      {researcher.phone_number && (
                        <p className="text-sm text-gray-600">
                          <span className="font-medium">Phone:</span> {researcher.phone_number}
                        </p>
                      )}
                      {researcher.address && (
                        <p className="text-sm text-gray-600">
                          <span className="font-medium">Address:</span> {researcher.address}
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="flex flex-col items-end gap-2">
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => handleTogglePromoted(researcher.id, researcher.promoted)}
                      >
                        {researcher.promoted ? 'Unpromote' : 'Promote'}
                      </Button>
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => handleToggleActiveLead(researcher.id, researcher.is_active_lead)}
                      >
                        {researcher.is_active_lead ? 'Deactivate' : 'Activate'}
                      </Button>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => handleViewDetails(researcher.id)}
                      >
                        View Details
                      </Button>
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => handleDelete(researcher.id)}
                      >
                        Delete
                      </Button>
                    </div>
                  </div>
                </div>

                {/* Notes */}
                {researcher.notes && (
                  <div className="bg-gray-50 p-3 rounded-lg">
                    <p className="text-sm text-gray-700">
                      <span className="font-medium">Notes:</span> {researcher.notes}
                    </p>
                  </div>
                )}
              </div>
            </Card>
          ))}

          {filteredResearchers.length === 0 && (
            <div className="text-center py-12 bg-white rounded-lg shadow">
              <div className="text-gray-400 text-6xl mb-4">🔍</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No researchers found</h3>
              <p className="text-gray-600">Try adjusting your search or filters</p>
            </div>
          )}
        </div>
      </div>
    </MainLayout>
  );
}