'use client';

import React, { useState } from 'react';
import { ContactFormData, LeadClassification } from '@/lib/types/contact';
import { Input } from '../ui/Input';
import { Textarea } from '../ui/Textarea';
import { Select } from '../ui/Select';
import { Button } from '../ui/Button';

/** Props interface for the ContactForm component. */
interface ContactFormProps {
  /** Optional initial data to populate the form. */
  initialData?: Partial<ContactFormData>;
  /** Callback function called when the form is submitted with valid data. */
  onSubmit: (data: ContactFormData) => Promise<void>;
  /** Optional callback function called when the cancel button is clicked. */
  onCancel?: () => void;
  /** Label for the submit button. Defaults to 'Submit'. */
  submitLabel?: string;
}

/** Available lead classification options for the dropdown. */
const leadClassOptions = [
  { value: 'New', label: 'New' },
  { value: 'Contacted', label: 'Contacted' },
  { value: 'Growing Interest', label: 'Growing Interest' },
  { value: 'Leading', label: 'Leading' },
  { value: 'Converted', label: 'Converted' },
  { value: 'Cold', label: 'Cold' },
  { value: 'Dying', label: 'Dying' },
];

/**
 * Form component for creating and editing contacts.
 *
 * This component provides a comprehensive form for contact data including name,
 * email, phone, company, lead classification, address, and notes. It handles
 * form validation, error display, and loading states during submission.
 *
 * @example
 * ```tsx
 * <ContactForm
 *   onSubmit={handleSubmit}
 *   onCancel={() => setShowForm(false)}
 *   submitLabel="Create Contact"
 * />
 * ```
 */
export function ContactForm({
  initialData,
  onSubmit,
  onCancel,
  submitLabel = 'Submit',
}: ContactFormProps) {
  /** Current form data state. */
  const [formData, setFormData] = useState<ContactFormData>({
    Full_name: initialData?.Full_name || '',
    email: initialData?.email || '',
    phone_number: initialData?.phone_number || '',
    company: initialData?.company || '',
    lead_class: initialData?.lead_class || 'New',
    notes: initialData?.notes || '',
    address: initialData?.address || '',
  });

  /** Validation error messages for each form field. */
  const [errors, setErrors] = useState<Record<string, string>>({});
  /** Loading state during form submission. */
  const [loading, setLoading] = useState(false);

  /**
   * Validates the form data.
   *
   * @returns True if form is valid, false otherwise.
   */
  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.Full_name.trim()) {
      newErrors.Full_name = 'Name is required';
    }
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Invalid email format';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  /**
   * Handles form submission.
   *
   * Validates the form, sets loading state, and calls the onSubmit callback.
   * If validation fails, submission is prevented.
   *
   * @param e - The form submission event.
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) return;

    setLoading(true);
    try {
      await onSubmit(formData);
    } catch (error) {
      console.error('Form submission error:', error);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Creates a change handler for a specific form field.
   *
   * Updates the form data state and clears any validation errors for the
   * changed field.
   *
   * @param field - The key of the form field to update.
   * @returns A change event handler function.
   */
  const handleChange = (field: keyof ContactFormData) => (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    setFormData({ ...formData, [field]: e.target.value });
    if (errors[field]) {
      setErrors({ ...errors, [field]: '' });
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        label="Full Name"
        value={formData.Full_name}
        onChange={handleChange('Full_name')}
        error={errors.Full_name}
        required
      />

      <Input
        label="Email"
        type="email"
        value={formData.email}
        onChange={handleChange('email')}
        error={errors.email}
        required
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
          {loading ? 'Submitting...' : submitLabel}
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
