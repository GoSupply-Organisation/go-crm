'use client';

import React, { useState } from 'react';
import { Contact } from '@/lib/types/contact';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';

/** Props interface for the ContactList component. */
interface ContactListProps {
  /** Array of contacts to display. */
  contacts: Contact[];
  /** Whether the list is in a loading state. */
  loading?: boolean;
  /** Callback when a contact is clicked. */
  onContactClick?: (contact: Contact) => void;
  /** Callback when the email button is clicked for a contact. */
  onSendEmail?: (contactId: number) => void;
  /** Callback when the SMS button is clicked for a contact. */
  onSendSMS?: (contactId: number) => void;
  /** Callback when the more info button is clicked for a contact. */
  onMoreInfo?: (contactId: number) => void;
  /** Callback when the edit button is clicked for a contact. */
  onEdit?: (contactId: number) => void;
}

/** Color mapping for lead classification badges. */
const leadClassColors: Record<string, 'gray' | 'blue' | 'yellow' | 'orange' | 'purple' | 'green' | 'red'> = {
  'New': 'blue',
  'Contacted': 'yellow',
  'Growing Interest': 'orange',
  'Leading': 'purple',
  'Converted': 'green',
  'Cold': 'gray',
  'Dying': 'red',
};

/**
 * List component for displaying contacts with filtering and actions.
 *
 * This component renders a grid of contact cards with search and filter
 * capabilities. Each contact card displays key information and provides
 * action buttons for email, SMS, edit, and more info operations.
 *
 * @example
 * ```tsx
 * <ContactList
 *   contacts={contacts}
 *   onSendEmail={(id) => openEmailModal(id)}
 *   onSendSMS={(id) => openSMSModal(id)}
 * />
 * ```
 */
export function ContactList({ contacts, loading, onContactClick, onSendEmail, onSendSMS, onMoreInfo, onEdit }: ContactListProps) {
  /** Search term for filtering contacts. */
  const [searchTerm, setSearchTerm] = useState('');
  /** Selected lead class filter. Empty string means no filter. */
  const [filterClass, setFilterClass] = useState<string>('');

  /**
   * Filtered contacts based on search term and lead class.
   * Matches against name, email, and company fields.
   */
  const filteredContacts = contacts.filter((contact) => {
    const matchesSearch =
      contact.Full_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      contact.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      contact.company?.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesFilter = !filterClass || contact.lead_class === filterClass;

    return matchesSearch && matchesFilter;
  });

  if (loading) {
    return <div className="text-center py-8">Loading contacts...</div>;
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row gap-4 mb-6">
        <input
          type="text"
          placeholder="Search contacts..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <select
          value={filterClass}
          onChange={(e) => setFilterClass(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All Classes</option>
          <option value="New">New</option>
          <option value="Contacted">Contacted</option>
          <option value="Growing Interest">Growing Interest</option>
          <option value="Leading">Leading</option>
          <option value="Converted">Converted</option>
          <option value="Cold">Cold</option>
          <option value="Dying">Dying</option>
        </select>
      </div>

      <div className="grid gap-4">
        {filteredContacts.map((contact) => (
          <div
            key={contact.id}
            className="bg-white p-4 rounded-lg shadow hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h3 className="font-semibold text-lg text-gray-900">{contact.Full_name}</h3>
                <p className="text-sm text-gray-600">{contact.email}</p>
                <p className="text-sm text-gray-600">{contact.company}</p>
              </div>
              <div className="flex flex-col items-end gap-2">
                <Badge variant={leadClassColors[contact.lead_class]}>{contact.lead_class}</Badge>
                <div className="flex gap-2 mt-2">
                  <Button
                    size="sm"
                    variant="secondary"
                    onClick={(e) => {
                      e.stopPropagation();
                      onSendEmail?.(contact.id);
                    }}
                  >
                    Email
                  </Button>
                  <Button
                    size="sm"
                    variant="secondary"
                    onClick={(e) => {
                      e.stopPropagation();
                      onSendSMS?.(contact.id);
                    }}
                  >
                    SMS
                  </Button>
                  <Button
                    size="sm"
                    variant="secondary"
                    onClick={(e) => {
                      e.stopPropagation();
                      onMoreInfo?.(contact.id);
                    }}
                  >
                    More Info
                  </Button>
                  <Button
                    size="sm"
                    variant="secondary"
                    onClick={(e) => {
                      e.stopPropagation();
                      onEdit?.(contact.id);
                    }}
                  >
                    Edit
                  </Button>
                </div>
              </div>
            </div>
            {contact.phone_number && (
              <p className="text-sm text-gray-500 mt-2">{contact.phone_number}</p>
            )}
          </div>
        ))}
      </div>

      {filteredContacts.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          No contacts found matching your criteria.
        </div>
      )}
    </div>
  );
}
