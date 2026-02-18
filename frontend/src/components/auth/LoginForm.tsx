'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/components/auth/AuthContext';

/**
 * Custom hook for managing login form state and logic.
 *
 * This hook encapsulates the form data management, validation,
 * authentication logic, and navigation for the login form.
 * It returns form state, error messages, loading state, and
 * event handlers for form interactions.
 *
 * @returns An object containing form state and handlers:
 *   - formData: Current email and password values
 *   - error: Error message if login failed
 *   - loading: Boolean indicating loading state
 *   - handleChange: Handler for input changes
 *   - handleSubmit: Handler for form submission
 */
export function useLoginForm() {
  /** Next.js router for navigation after successful login. */
  const router = useRouter();
  /** Authentication context for login functionality. */
  const { login } = useAuth();

  /** Current form data state containing email and password. */
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  /** Error message to display if login fails. */
  const [error, setError] = useState('');
  /** Loading state during login process. */
  const [loading, setLoading] = useState(false);

  /**
   * Handles changes to form input fields.
   *
   * Updates the form data state and clears any existing error
   * when the user starts typing again.
   *
   * @param e - The change event from the input field.
   */
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    setError('');
  };

  /**
   * Handles form submission for user login.
   *
   * Validates credentials through the authentication context,
   * navigates to dashboard on success, and displays error
   * message on failure.
   *
   * @param e - The form submission event.
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(formData.email, formData.password);
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return {
    formData,
    error,
    loading,
    handleChange,
    handleSubmit,
  };
}
