'use client';

import React, { useState } from 'react';
import { MainLayout } from '@/components/layout/MainLayout';
import { ContactList } from '@/components/contacts/ContactList';
import { useContacts } from '@/lib/hooks/useContacts';
import { Contact } from '@/lib/types/contact';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';
import { ContactForm } from '@/components/contacts/ContactForm';
import { useContactOperations } from '@/lib/hooks/useContacts';
import { SendEmailForm } from '@/components/communications/EmailForm';
import { SendSMSForm } from '@/components/communications/SMSForm';
import { EditContactForm } from '@/components/communications/EditForm';
import { communicationsApi} from '@/lib/api/communications';
import { contactsApi } from '@/lib/api/contacts';

export default function ContactsPage() {
  const { contacts, loading, error, refetch } = useContacts();
  const { createContact } = useContactOperations();
  const [showModal, setShowModal] = useState(false);
  const [showEmailModal, setShowEmailModal] = useState(false);
  const [showSMSModal, setShowSMSModal] = useState(false);
  const [showMoreInfoModal, setShowMoreInfoModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedContactId, setSelectedContactId] = useState<number | null>(null);
  const [selectedContact, setSelectedContact] = useState<Contact | null>(null);
  const [moreInfoData, setMoreInfoData] = useState<any>(null);
  const [loadingMoreInfo, setLoadingMoreInfo] = useState(false);

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

  const handleMoreInfo = async (contactId: number) => {
    try {
      setLoadingMoreInfo(true);
      const contact = contacts.find(c => c.id === contactId);
      setSelectedContact(contact || null);
      const data = await contactsApi.getMoreInfoById(contactId);
      setMoreInfoData(data);
      setShowMoreInfoModal(true);
    } catch (error) {
      console.error('Failed to fetch more info:', error);
      alert('Failed to fetch more info. Please try again.');
    } finally {
      setLoadingMoreInfo(false);
    }
  };

  const handleEdit = (contactId: number) => {
    const contact = contacts.find(c => c.id === contactId);
    if (contact) {
      setSelectedContactId(contactId);
      setSelectedContact(contact);
      setShowEditModal(true);
    }
  };

  const handleUpdateContact = async (data: any) => {
    if (!selectedContactId) return;

    try {
      await contactsApi.updateContact(selectedContactId, data);
      setShowEditModal(false);
      setSelectedContact(null);
      setSelectedContactId(null);
      refetch();
      alert('Contact updated successfully!');
    } catch (error) {
      console.error('Failed to update contact:', error);
      alert('Failed to update contact. Please try again.');
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
            onSendEmail={(contactId) => {
              setSelectedContactId(contactId);
              setShowEmailModal(true);
            }}
            onSendSMS={(contactId) => {
              setSelectedContactId(contactId);
              setShowSMSModal(true);
            }}
            onMoreInfo={handleMoreInfo}
            onEdit={handleEdit}
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

        <Modal isOpen={showMoreInfoModal} onClose={() => {
          setShowMoreInfoModal(false);
          setSelectedContact(null);
          setMoreInfoData(null);
        }} title="More Information">
          {loadingMoreInfo ? (
            <div className="text-center py-4">Loading...</div>
          ) : moreInfoData ? (
            <div className="space-y-4">
              {selectedContact && (
                <div className="border-b pb-4">
                  <h3 className="text-xl font-semibold text-gray-900">{selectedContact.Full_name}</h3>
                  <p className="text-gray-600">{selectedContact.company}</p>
                  <span className="inline-block mt-2 px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                    {selectedContact.lead_class}
                  </span>
                </div>
              )}
              <div className="grid gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                  <p className="text-gray-900">{moreInfoData.email || selectedContact?.email}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                  <p className="text-gray-900">{moreInfoData.phone_number || selectedContact?.phone_number}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Address</label>
                  <p className="text-gray-900">{moreInfoData.address || 'No address provided'}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
                  <p className="text-gray-900 whitespace-pre-wrap">{moreInfoData.notes || 'No notes provided'}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Created</label>
                  <p className="text-gray-900">{new Date(moreInfoData.created_at).toLocaleDateString()}</p>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-4 text-gray-500">No information available</div>
          )}
        </Modal>

        <Modal isOpen={showEditModal} onClose={() => {
          setShowEditModal(false);
          setSelectedContact(null);
        }} title="Edit Contact">
          {selectedContact && (
            <EditContactForm
              contact={selectedContact}
              onSubmit={handleUpdateContact}
              onCancel={() => {
                setShowEditModal(false);
                setSelectedContact(null);
              }}
            />
          )}
        </Modal>
      </div>
    </MainLayout>
  );
}