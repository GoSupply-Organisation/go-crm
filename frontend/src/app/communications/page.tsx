'use client';

import React, { useState } from 'react';
import { MainLayout } from '@/components/layout/MainLayout';
import { ContactList } from '@/components/contacts/ContactList';
import { useContacts } from '@/lib/hooks/useContacts';
import { Contact } from '@/lib/types/contacts';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';
import { ContactForm } from '@/components/contacts/ContactForm';
import { useContactOperations } from '@/lib/hooks/useContacts';

export default function ContactsPage() {
  const { contacts, loading, error, refetch } = useContacts();
  const { createContact } = useContactOperations();
  const router = useRouter();
  const [showModal, setShowModal] = useState(false);

  const handleContactClick = (contact: Contact) => {
    router.push(`/contacts/${contact.id}`);
  };

  const handleCreateContact = async (data: any) => {
    try {
      await createContact(data);
      setShowModal(false);
      refetch();
    } catch (error) {
      console.error('Failed to create contact:', error);
    }
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold text-gray-900">Contacts</h1>
          <Button onClick={() => setShowModal(true)}>Add Contact</Button>
        </div>

        {error ? (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        ) : (
          <ContactList
            contacts={contacts}
            loading={loading}
            onContactClick={handleContactClick}
          />
        )}

        <Modal isOpen={showModal} onClose={() => setShowModal(false)} title="Add New Contact">
          <ContactForm
            onSubmit={handleCreateContact}
            onCancel={() => setShowModal(false)}
            submitLabel="Create Contact"
          />
        </Modal>
      </div>
    </MainLayout>
  );
}