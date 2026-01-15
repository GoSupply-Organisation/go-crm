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
import { SendEmailForm } from '@/components/communications/EmailForm';
import { SendSMSForm } from '@/components/communications/SMSForm';
import { communicationsApi } from '@/lib/api/communications';

export default function ContactsPage() {
  const { contacts, loading, error, refetch } = useContacts();
  const { createContact } = useContactOperations();
  const router = useRouter();
  const [showModal, setShowModal] = useState(false);
  const [showEmailModal, setShowEmailModal] = useState(false);
  const [showSMSModal, setShowSMSModal] = useState(false);
  const [selectedContactId, setSelectedContactId] = useState<number | null>(null);

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

  const handleSendEmail = async (data: { subject: string; message: string }) => {
    if (!selectedContactId) return;

    try {
      await communicationsApi.sendEmail(selectedContactId, data);
      setShowEmailModal(false);
      setSelectedContactId(null);
      alert('Email sent successfully!');
    } catch (error) {
      console.error('Failed to send email:', error);
      alert('Failed to send email. Please try again.');
    }
  };

  const handleSendSMS = async (data: { message: string }) => {
    if (!selectedContactId) return;

    try {
      await communicationsApi.sendSMS(selectedContactId, data);
      setShowSMSModal(false);
      setSelectedContactId(null);
      alert('SMS sent successfully!');
    } catch (error) {
      console.error('Failed to send SMS:', error);
      alert('Failed to send SMS. Please try again.');
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
            onSendEmail={(contactId) => {
              setSelectedContactId(contactId);
              setShowEmailModal(true);
            }}
            onSendSMS={(contactId) => {
              setSelectedContactId(contactId);
              setShowSMSModal(true);
            }}
          />
        )}

        <Modal isOpen={showModal} onClose={() => setShowModal(false)} title="Add New Contact">
          <ContactForm
            onSubmit={handleCreateContact}
            onCancel={() => setShowModal(false)}
            submitLabel="Create Contact"
          />
        </Modal>

        <Modal isOpen={showEmailModal} onClose={() => {
          setShowEmailModal(false);
          setSelectedContactId(null);
        }} title="Send Email">
          {selectedContactId && (
            <SendEmailForm
              contactId={selectedContactId}
              onSubmit={handleSendEmail}
              onCancel={() => {
                setShowEmailModal(false);
                setSelectedContactId(null);
              }}
            />
          )}
        </Modal>

        <Modal isOpen={showSMSModal} onClose={() => {
          setShowSMSModal(false);
          setSelectedContactId(null);
        }} title="Send SMS">
          {selectedContactId && (
            <SendSMSForm
              contactId={selectedContactId}
              onSubmit={handleSendSMS}
              onCancel={() => {
                setShowSMSModal(false);
                setSelectedContactId(null);
              }}
            />
          )}
        </Modal>
      </div>
    </MainLayout>
  );
}