'use client';

import React, { useState } from 'react';
import { Textarea } from '../ui/Textarea';
import { Button } from '../ui/Button';

interface SendSMSFormData {
  message: string;
}

interface SendSMSFormProps {
  contactId: number;
  onSubmit: (data: SendSMSFormData) => Promise<void>;
  onCancel?: () => void;
}

export function SendSMSForm({ contactId, onSubmit, onCancel }: SendSMSFormProps) {
  const [formData, setFormData] = useState<SendSMSFormData>({
    message: '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.message.trim()) {
      newErrors.message = 'Message is required';
    } else if (formData.message.length > 160) {
      newErrors.message = 'Message must be 160 characters or less';
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
      console.error('SMS sending error:', error);
    } finally {
      setLoading(false);
    }
  };

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
        maxLength={160}
        required
      />

      <div className="text-sm text-gray-500 text-right">
        {formData.message.length}/160 characters
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