'use client';

import React, { useState } from 'react';
import { Input } from '../ui/Input';
import { Textarea } from '../ui/Textarea';
import { Button } from '../ui/Button';

/** Data structure for email sending form. */
interface SendEmailFormData {
  /** Email subject line. */
  subject: string;
  /** Email body message. */
  message: string;
}

/** Props interface for the SendEmailForm component. */
interface SendEmailFormProps {
  /** ID of the contact to send email to. */
  contactId: number;
  /** Callback function called when form is submitted with valid data. */
  onSubmit: (data: SendEmailFormData) => Promise<void>;
  /** Optional callback function called when the cancel button is clicked. */
  onCancel?: () => void;
}

/**
 * Form component for sending emails to contacts.
 *
 * This component provides a form with subject and message fields for
 * composing emails to specific contacts. It handles form validation
 * and loading states during email sending.
 *
 * @example
 * ```tsx
 * <SendEmailForm
 *   contactId={contact.id}
 *   onSubmit={async (data) => {
 *     await sendEmail(contactId, data);
 *     closeModal();
 *   }}
 *   onCancel={closeModal}
 * />
 * ```
 */
export function SendEmailForm({ contactId, onSubmit, onCancel }: SendEmailFormProps) {
  /** Current form data state. */
  const [formData, setFormData] = useState<SendEmailFormData>({
    subject: '',
    message: '',
  });

  /** Validation error messages for each form field. */
  const [errors, setErrors] = useState<Record<string, string>>({});
  /** Loading state during email sending. */
  const [loading, setLoading] = useState(false);

  /**
   * Validates the form data.
   *
   * Ensures both subject and message fields are not empty.
   *
   * @returns True if form is valid, false otherwise.
   */
  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.subject.trim()) {
      newErrors.subject = 'Subject is required';
    }
    if (!formData.message.trim()) {
      newErrors.message = 'Message is required';
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
      console.error('Email sending error:', error);
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
  const handleChange = (field: keyof SendEmailFormData) => (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    setFormData({ ...formData, [field]: e.target.value });
    if (errors[field]) {
      setErrors({ ...errors, [field]: '' });
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="text-sm text-gray-600 mb-4">
        Sending email to contact ID: {contactId}
      </div>

      <Input
        label="Subject"
        value={formData.subject}
        onChange={handleChange('subject')}
        error={errors.subject}
        required
      />

      <Textarea
        label="Message"
        value={formData.message}
        onChange={handleChange('message')}
        error={errors.message}
        rows={6}
        required
      />

      <div className="flex space-x-3 pt-4">
        <Button type="submit" disabled={loading}>
          {loading ? 'Sending...' : 'Send Email'}
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
