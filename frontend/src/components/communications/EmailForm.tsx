'use client';

import React, { useState } from 'react';
import { Input } from '../ui/Input';
import { Textarea } from '../ui/Textarea';
import { Button } from '../ui/Button';

interface SendEmailFormData {
  subject: string;
  message: string;
}

interface SendEmailFormProps {
  contactId: number;
  onSubmit: (data: SendEmailFormData) => Promise<void>;
  onCancel?: () => void;
}

export function SendEmailForm({ contactId, onSubmit, onCancel }: SendEmailFormProps) {
  const [formData, setFormData] = useState<SendEmailFormData>({
    subject: '',
    message: '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);

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