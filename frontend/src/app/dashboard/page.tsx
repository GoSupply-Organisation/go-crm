'use client';

import React from 'react';
import { MainLayout } from '@/components/layout/MainLayout';
import { useContacts } from '@/lib/hooks/useContacts';
import { useTodos } from '@/lib/hooks/useTodos';
import { useResearchPipeline } from '@/lib/hooks/useResearch';
import { Card } from '@/components/ui/Card';
import { Loader } from '@/components/ui/Loader';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';

export default function DashboardPage() {
  
  const { contacts, loading: contactsLoading } = useContacts();
  const { todos, loading: todosLoading } = useTodos();
  const { stagedLeads, activeLeads, loading: researchLoading } = useResearchPipeline();

  const totalStaged = stagedLeads.apex.length + stagedLeads.super.length;
  const totalActive = activeLeads.apex.length + activeLeads.super.length;

  const recentContacts = contacts.slice(0, 5);
  const pendingTodos = todos.filter((todo) => !todo.completed).slice(0, 5);

  return (
    <MainLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white">
            <div className="text-3xl font-bold">{contacts.length}</div>
            <div className="text-blue-100">Total Contacts</div>
          </Card>
          <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white">
            <div className="text-3xl font-bold">{totalActive}</div>
            <div className="text-green-100">Active Leads</div>
          </Card>
          <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
            <div className="text-3xl font-bold">{totalStaged}</div>
            <div className="text-purple-100">Staged Leads</div>
          </Card>
          <Card className="bg-gradient-to-br from-orange-500 to-orange-600 text-white">
            <div className="text-3xl font-bold">{pendingTodos.length}</div>
            <div className="text-orange-100">Pending Tasks</div>
          </Card>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Recent Contacts */}
          <Card title="Recent Contacts" actions={
            <Link href="/contacts">
              <Button variant="ghost" size="sm">View All</Button>
            </Link>
          }>
            {contactsLoading ? (
              <Loader />
            ) : recentContacts.length > 0 ? (
              <div className="space-y-3">
                {recentContacts.map((contact) => (
                  <div
                    key={contact.id}
                    className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg cursor-pointer"
                  >
                    <div>
                      <h4 className="font-medium text-gray-900">{contact.Full_name}</h4>
                      <p className="text-sm text-gray-600">{contact.company}</p>
                    </div>
                    <span className="text-sm text-blue-600">{contact.lead_class}</span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-4 text-gray-500">No contacts yet</div>
            )}
          </Card>

          {/* Pending Todos */}
          <Card title="Pending Tasks" actions={
            <Link href="/todos">
              <Button variant="ghost" size="sm">View All</Button>
            </Link>
          }>
            {todosLoading ? (
              <Loader />
            ) : pendingTodos.length > 0 ? (
              <div className="space-y-3">
                {pendingTodos.map((todo) => (
                  <div
                    key={todo.id}
                    className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg"
                  >
                    <div>
                      <h4 className="font-medium text-gray-900">{todo.title}</h4>
                      <p className="text-sm text-gray-600">{todo.description}</p>
                    </div>
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      todo.priority === 'high' ? 'bg-red-100 text-red-800' :
                      todo.priority === 'medium' ? 'bg-blue-100 text-blue-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {todo.priority}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-4 text-gray-500">No pending tasks</div>
            )}
          </Card>
        </div>

        {/* Research Pipeline Preview */}
        <Card title="Research Pipeline Overview" actions={
          <Link href="/research">
            <Button variant="ghost" size="sm">View Pipeline</Button>
          </Link>
        }>
          {researchLoading ? (
            <Loader />
          ) : (
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">{totalStaged}</div>
                <div className="text-sm text-blue-800">Staged Leads</div>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">{totalActive}</div>
                <div className="text-sm text-green-800">Active Leads</div>
              </div>
            </div>
          )}
        </Card>
      </div>
    </MainLayout>
  );
}