'use client';

import React, { useState } from 'react';
import { Textarea } from '../ui/Textarea';
import { Button } from '../ui/Button';

/** Data structure for SMS sending form. */
interface SendSMSFormData {
  /** SMS message content. */
  message: string;
}

/** Props interface for the SendSMSForm component. */
interface SendSMSFormProps {
  /** ID of the contact to send SMS to. */
  contactId: number;
  /** Callback function called when form is submitted with valid data. */
  onSubmit: (data: SendSMSFormData) => Promise<void>;
  /** Optional callback function called when the cancel button is clicked. */
  onCancel?: () => void;
}

/** Maximum character limit for SMS messages. */
const SMS_MAX_LENGTH = 160;

/**
 * Form component for sending SMS messages to contacts.
 *
 * This component provides a form with a message field for composing
 * SMS messages to specific contacts. It enforces the 160 character
 * limit for SMS and handles loading states during message sending.
 *
 * @example
 * ```tsx
 * <SendSMSForm
 *   contactId={contact.id}
 *   onSubmit={async (data) => {
 *     await sendSMS(contactId, data);
 *     closeModal();
 *   }}
 *   onCancel={closeModal}
 * />
 * ```
 */
export function SendSMSForm({ contactId, onSubmit, onCancel }: SendSMSFormProps) {
  /** Current form data state. */
  const [formData, setFormData] = useState<SendSMSFormData>({
    message: '',
  });

  /** Validation error messages for the message field. */
  const [errors, setErrors] = useState<Record<string, string>>({});
  /** Loading state during SMS sending. */
  const [loading, setLoading] = useState(false);

  /**
   * Validates the form data.
   *
   * Ensures the message field is not empty and does not exceed
   * the 160 character SMS limit.
   *
   * @returns True if form is valid, false otherwise.
   */
  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.message.trim()) {
      newErrors.message = 'Message is required';
    } else if (formData.message.length > SMS_MAX_LENGTH) {
      newErrors.message = 'Message must be 160 characters or less';
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
      console.error('SMS sending error:', error);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Creates a change handler for the message field.
   *
   * Updates the form data state and clears any validation errors.
   *
   * @returns A change event handler function.
   */
  const handleChange = (field: keyof SendSMSFormData) => (
    e: React.ChangeEvent<HTMLTextAreaElement>
  ) => {
    setFormData({ ...formData, [field]: e.target.value });
    if (errors[field]) {
      setErrors({ ...errors, [field]: '' });
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="text-sm text-gray-600 mb-4">
        Sending SMS to contact ID: {contactId}
      </div>

      <Textarea
        label="Message"
        value={formData.message}
        onChange={handleChange('message')}
        error={errors.message}
        rows={4}
        placeholder="Enter your SMS message (max 160 characters)"
        maxLength={SMS_MAX_LENGTH}
        required
      />

      <div className="text-sm text-gray-500 text-right">
        {formData.message.length}/{SMS_MAX_LENGTH} characters
      </div>

      <div className="flex space-x-3 pt-4">
        <Button type="submit" disabled={loading}>
          {loading ? 'Sending...' : 'Send SMS'}
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
