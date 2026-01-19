'use client';

import React, { useState } from 'react';
import { Contact } from '@/lib/types/contact';
import { Input } from '../ui/Input';
import { Textarea } from '../ui/Textarea';
import { Select } from '../ui/Select';
import { Button } from '../ui/Button';
import { EditContactFormData, EditContactFormProps } from '@/lib/types/contact';


const leadClassOptions = [
  { value: 'New', label: 'New' },
  { value: 'Contacted', label: 'Contacted' },
  { value: 'Growing Interest', label: 'Growing Interest' },
  { value: 'Leading', label: 'Leading' },
  { value: 'Converted', label: 'Converted' },
  { value: 'Cold', label: 'Cold' },
  { value: 'Dying', label: 'Dying' },
];

export function EditContactForm({ contact, onSubmit, onCancel }: EditContactFormProps) {
  const [formData, setFormData] = useState<EditContactFormData>({
    Full_name: contact.Full_name ?? "",
    company: contact.company ?? "",
    lead_class: contact.lead_class ?? "",
    email: contact.email ?? "",
    phone_number: contact.phone_number ?? "",
    address: contact.address ?? "",
    notes: contact.notes ?? "",
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (formData.email && !/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Invalid email format';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) return;

    setLoading(true);
    try {
      await onSubmit(formData);
    } catch (error) {
      console.error('Edit contact error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field: keyof EditContactFormData) => (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    setFormData({ ...formData, [field]: e.target.value });
    if (errors[field]) {
      setErrors({ ...errors, [field]: '' });
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="text-sm text-gray-600 mb-4">
        Editing contact: {contact.Full_name}
      </div>

      <Input
        label="Full Name"
        value={formData.Full_name}
        onChange={handleChange('Full_name')}
      />

      <Input
        label="Email"
        type="email"
        value={formData.email}
        onChange={handleChange('email')}
        error={errors.email}
      />

      <Input
        label="Phone Number"
        type="tel"
        value={formData.phone_number}
        onChange={handleChange('phone_number')}
      />

      <Input
        label="Company"
        value={formData.company}
        onChange={handleChange('company')}
      />

      <Select
        label="Lead Classification"
        options={leadClassOptions}
        value={formData.lead_class}
        onChange={handleChange('lead_class')}
      />

      <Input
        label="Address"
        value={formData.address}
        onChange={handleChange('address')}
      />

      <Textarea
        label="Notes"
        value={formData.notes}
        onChange={handleChange('notes')}
        rows={3}
      />

      <div className="flex space-x-3 pt-4">
        <Button type="submit" disabled={loading}>
          {loading ? 'Updating...' : 'Update Contact'}
        </Button>
        {onCancel && (
          <Button type="button" variant="secondary" onClick={onCancel}>
            Cancel
          </Button>
        )}
      </div>
    </form>
  );
}