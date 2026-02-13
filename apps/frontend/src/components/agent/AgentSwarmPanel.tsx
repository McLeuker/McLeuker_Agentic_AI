"""
Agent Swarm Panel - Frontend UI for 100+ Agent Ecosystem
=======================================================

Features:
- Agent browser and search
- Task submission interface
- Real-time execution monitoring
- Agent performance metrics
- Swarm session management
"""

import React, { useState, useEffect, useCallback } from 'react';
import {
  Search,
  Play,
  Pause,
  StopCircle,
  CheckCircle,
  XCircle,
  Loader2,
  Bot,
  Users,
  Activity,
  BarChart3,
  MessageSquare,
  ChevronDown,
  ChevronRight,
  Filter,
  Grid,
  List,
  Sparkles,
  Zap,
  Clock,
  TrendingUp,
} from 'lucide-react';

// Types
export interface AgentDefinition {
  name: string;
  description: string;
  category: string;
  subcategory: string;
  capabilities: string[];
  tags: string[];
  temperature: number;
}

export interface AgentTask {
  id: string;
  description: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  assigned_agent?: string;
  priority: number;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  result?: any;
  error?: string;
}

export interface AgentInstance {
  instance_id: string;
  agent_name: string;
  status: 'idle' | 'initializing' | 'ready' | 'busy' | 'error';
  current_tasks: string[];
  total_tasks_completed: number;
  health_score: number;
}

export interface SwarmMetrics {
  total_agents: number;
  active_agents: number;
  total_tasks: number;
  completed_tasks: number;
  failed_tasks: number;
  avg_execution_time: number;
}

interface AgentSwarmPanelProps {
  agents: AgentDefinition[];
  tasks: AgentTask[];
  instances: AgentInstance[];
  metrics: SwarmMetrics;
  onSubmitTask: (description: string, agentName?: string) => Promise<string>;
  onCancelTask: (taskId: string) => Promise<void>;
  onRefresh: () => Promise<void>;
  className?: string;
}

// Category colors
const categoryColors: Record<string, string> = {
  content: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  data: 'bg-green-500/20 text-green-400 border-green-500/30',
  development: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
  business: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
  research: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30',
  media: 'bg-pink-500/20 text-pink-400 border-pink-500/30',
  operations: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
  legal: 'bg-red-500/20 text-red-400 border-red-500/30',
  healthcare: 'bg-teal-500/20 text-teal-400 border-teal-500/30',
};

// Status icons
const statusIcons = {
  pending: Clock,
  running: Loader2,
  completed: CheckCircle,
  failed: XCircle,
  cancelled: StopCircle,
};

const statusColors = {
  pending: 'text-gray-400',
  running: 'text-blue-400 animate-spin',
  completed: 'text-green-400',
  failed: 'text-red-400',
  cancelled: 'text-gray-500',
};

// Agent Card Component
const AgentCard: React.FC<{
  agent: AgentDefinition;
  isSelected: boolean;
  onClick: () => void;
}> = ({ agent, isSelected, onClick }) => {
  return (
    <div
      onClick={onClick}
      className={`
        p-4 rounded-xl border cursor-pointer transition-all duration-200
        ${isSelected 
          ? 'border-blue-500 bg-blue-500/10 ring-1 ring-blue-500/50' 
          : 'border-gray-800 bg-gray-900/50 hover:border-gray-700 hover:bg-gray-800/50'
        }
      `}
    >
      <div className="flex items-start gap-3">
        <div className={`
          w-10 h-10 rounded-lg flex items-center justify-center
          ${categoryColors[agent.category] || categoryColors.operations}
        `}>
          <Bot className="w-5 h-5" />
        </div>
        
        <div className="flex-1 min-w-0">
          <h4 className="font-medium text-gray-200 truncate">{agent.name}</h4>
          <p className="text-xs text-gray-500 mt-0.5 line-clamp-2">{agent.description}</p>
          
          <div className="flex flex-wrap gap-1 mt-2">
            <span className={`
              text-xs px-2 py-0.5 rounded-full border
              ${categoryColors[agent.category] || categoryColors.operations}
            `}>
              {agent.category}
            </span>
            {agent.tags.slice(0, 2).map((tag) => (
              <span
                key={tag}
                className="text-xs px-2 py-0.5 rounded-full bg-gray-800 text-gray-400"
              >
                {tag}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// Task Item Component
const TaskItem: React.FC<{
  task: AgentTask;
  onCancel: () => void;
}> = ({ task, onCancel }) => {
  const StatusIcon = statusIcons[task.status];
  
  return (
    <div className="p-3 rounded-lg border border-gray-800 bg-gray-900/30">
      <div className="flex items-center gap-3">
        <StatusIcon className={`w-4 h-4 ${statusColors[task.status]}`} />
        
        <div className="flex-1 min-w-0">
          <p className="text-sm text-gray-300 truncate">{task.description}</p>
          <div className="flex items-center gap-2 mt-1">
            {task.assigned_agent && (
              <span className="text-xs text-gray-500">{task.assigned_agent}</span>
            )}
            <span className="text-xs text-gray-600">
              {new Date(task.created_at).toLocaleTimeString()}
            </span>
          </div>
        </div>
        
        {task.status === 'running' && (
          <button
            onClick={onCancel}
            className="p-1.5 rounded-lg text-red-400 hover:bg-red-500/20 transition-colors"
          >
            <StopCircle className="w-4 h-4" />
          </button>
        )}
      </div>
      
      {task.result && (
        <div className="mt-2 p-2 rounded bg-gray-950 text-xs text-gray-400 max-h-20 overflow-auto">
          {typeof task.result === 'string' 
            ? task.result 
            : JSON.stringify(task.result, null, 2)}
        </div>
      )}
      
      {task.error && (
        <div className="mt-2 p-2 rounded bg-red-950/30 text-xs text-red-400">
          {task.error}
        </div>
      )}
    </div>
  );
};

// Metrics Card Component
const MetricsCard: React.FC<{
  title: string;
  value: string | number;
  icon: React.ElementType;
  trend?: string;
  trendUp?: boolean;
}> = ({ title, value, icon: Icon, trend, trendUp }) => (
  <div className="p-4 rounded-xl border border-gray-800 bg-gray-900/50">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-xs text-gray-500 uppercase tracking-wider">{title}</p>
        <p className="text-2xl font-semibold text-gray-200 mt-1">{value}</p>
        {trend && (
          <p className={`text-xs mt-1 ${trendUp ? 'text-green-400' : 'text-gray-500'}`}>
            {trend}
          </p>
        )}
      </div>
      <div className="w-10 h-10 rounded-lg bg-gray-800 flex items-center justify-center">
        <Icon className="w-5 h-5 text-gray-400" />
      </div>
    </div>
  </div>
);

// Main Agent Swarm Panel Component
export const AgentSwarmPanel: React.FC<AgentSwarmPanelProps> = ({
  agents,
  tasks,
  instances,
  metrics,
  onSubmitTask,
  onCancelTask,
  onRefresh,
  className = '',
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [taskInput, setTaskInput] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [activeTab, setActiveTab] = useState<'agents' | 'tasks' | 'metrics'>('agents');

  // Get unique categories
  const categories = ['all', ...Array.from(new Set(agents.map(a => a.category)))];

  // Filter agents
  const filteredAgents = agents.filter((agent) => {
    const matchesSearch = 
      agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      agent.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      agent.tags.some(t => t.toLowerCase().includes(searchQuery.toLowerCase()));
    
    const matchesCategory = selectedCategory === 'all' || agent.category === selectedCategory;
    
    return matchesSearch && matchesCategory;
  });

  // Submit task handler
  const handleSubmitTask = async () => {
    if (!taskInput.trim()) return;
    
    setIsSubmitting(true);
    try {
      await onSubmitTask(taskInput, selectedAgent || undefined);
      setTaskInput('');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className={`flex flex-col h-full bg-gray-950 ${className}`}>
      {/* Header */}
      <div className="p-4 border-b border-gray-800">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
              <Users className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-100">Agent Swarm</h2>
              <p className="text-xs text-gray-500">{agents.length} agents available</p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={() => onRefresh()}
              className="p-2 rounded-lg text-gray-400 hover:text-gray-200 hover:bg-gray-800 transition-colors"
            >
              <Activity className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Task Input */}
        <div className="mt-4">
          <div className="flex gap-2">
            <div className="flex-1 relative">
              <input
                type="text"
                value={taskInput}
                onChange={(e) => setTaskInput(e.target.value)}
                placeholder="Describe your task... (e.g., 'Write a blog post about AI')"
                className="w-full px-4 py-3 rounded-xl bg-gray-900 border border-gray-800 text-gray-200 placeholder-gray-500 focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50"
                onKeyDown={(e) => e.key === 'Enter' && handleSubmitTask()}
              />
              {selectedAgent && (
                <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs px-2 py-1 rounded-full bg-blue-500/20 text-blue-400">
                  {selectedAgent}
                </span>
              )}
            </div>
            <button
              onClick={handleSubmitTask}
              disabled={isSubmitting || !taskInput.trim()}
              className="px-6 py-3 rounded-xl bg-blue-600 text-white font-medium hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
            >
              {isSubmitting ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Zap className="w-4 h-4" />
              )}
              Execute
            </button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-800">
        {(['agents', 'tasks', 'metrics'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`
              flex-1 py-3 text-sm font-medium capitalize transition-colors
              ${activeTab === tab 
                ? 'text-blue-400 border-b-2 border-blue-400' 
                : 'text-gray-500 hover:text-gray-300'
              }
            `}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden">
        {activeTab === 'agents' && (
          <div className="h-full flex">
            {/* Agent List */}
            <div className="flex-1 overflow-y-auto p-4">
              {/* Filters */}
              <div className="flex items-center gap-3 mb-4">
                <div className="flex-1 relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search agents..."
                    className="w-full pl-10 pr-4 py-2 rounded-lg bg-gray-900 border border-gray-800 text-gray-200 placeholder-gray-500 focus:outline-none focus:border-blue-500/50"
                  />
                </div>
                
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="px-3 py-2 rounded-lg bg-gray-900 border border-gray-800 text-gray-200 focus:outline-none focus:border-blue-500/50"
                >
                  {categories.map((cat) => (
                    <option key={cat} value={cat}>
                      {cat === 'all' ? 'All Categories' : cat}
                    </option>
                  ))}
                </select>
                
                <div className="flex border border-gray-800 rounded-lg overflow-hidden">
                  <button
                    onClick={() => setViewMode('grid')}
                    className={`p-2 ${viewMode === 'grid' ? 'bg-gray-800 text-gray-200' : 'text-gray-500'}`}
                  >
                    <Grid className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setViewMode('list')}
                    className={`p-2 ${viewMode === 'list' ? 'bg-gray-800 text-gray-200' : 'text-gray-500'}`}
                  >
                    <List className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Agents Grid/List */}
              <div className={`
                ${viewMode === 'grid' 
                  ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3' 
                  : 'space-y-2'
                }
              `}>
                {filteredAgents.map((agent) => (
                  <AgentCard
                    key={agent.name}
                    agent={agent}
                    isSelected={selectedAgent === agent.name}
                    onClick={() => setSelectedAgent(
                      selectedAgent === agent.name ? null : agent.name
                    )}
                  />
                ))}
              </div>

              {filteredAgents.length === 0 && (
                <div className="text-center py-12">
                  <Bot className="w-12 h-12 mx-auto text-gray-600 mb-3" />
                  <p className="text-gray-500">No agents found</p>
                  <p className="text-sm text-gray-600">Try adjusting your search</p>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'tasks' && (
          <div className="h-full overflow-y-auto p-4">
            <div className="space-y-2">
              {tasks.length === 0 ? (
                <div className="text-center py-12">
                  <Clock className="w-12 h-12 mx-auto text-gray-600 mb-3" />
                  <p className="text-gray-500">No tasks yet</p>
                  <p className="text-sm text-gray-600">Submit a task to see it here</p>
                </div>
              ) : (
                tasks.map((task) => (
                  <TaskItem
                    key={task.id}
                    task={task}
                    onCancel={() => onCancelTask(task.id)}
                  />
                ))
              )}
            </div>
          </div>
        )}

        {activeTab === 'metrics' && (
          <div className="h-full overflow-y-auto p-4">
            <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
              <MetricsCard
                title="Total Agents"
                value={metrics.total_agents}
                icon={Bot}
              />
              <MetricsCard
                title="Active Agents"
                value={metrics.active_agents}
                icon={Activity}
                trend="Currently running"
                trendUp={true}
              />
              <MetricsCard
                title="Total Tasks"
                value={metrics.total_tasks}
                icon={MessageSquare}
              />
              <MetricsCard
                title="Completed"
                value={metrics.completed_tasks}
                icon={CheckCircle}
                trend={`${((metrics.completed_tasks / metrics.total_tasks) * 100 || 0).toFixed(1)}% success rate`}
                trendUp={true}
              />
              <MetricsCard
                title="Failed"
                value={metrics.failed_tasks}
                icon={XCircle}
              />
              <MetricsCard
                title="Avg Time"
                value={`${(metrics.avg_execution_time / 1000).toFixed(1)}s`}
                icon={Clock}
              />
            </div>

            {/* Active Instances */}
            <div className="mt-6">
              <h3 className="text-sm font-medium text-gray-300 mb-3">Active Instances</h3>
              <div className="space-y-2">
                {instances.map((instance) => (
                  <div
                    key={instance.instance_id}
                    className="p-3 rounded-lg border border-gray-800 bg-gray-900/30"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <Bot className="w-4 h-4 text-gray-500" />
                        <span className="text-sm text-gray-300">{instance.agent_name}</span>
                        <span className={`
                          text-xs px-2 py-0.5 rounded-full
                          ${instance.status === 'busy' ? 'bg-blue-500/20 text-blue-400' : ''}
                          ${instance.status === 'ready' ? 'bg-green-500/20 text-green-400' : ''}
                          ${instance.status === 'error' ? 'bg-red-500/20 text-red-400' : ''}
                        `}>
                          {instance.status}
                        </span>
                      </div>
                      <div className="flex items-center gap-4 text-xs text-gray-500">
                        <span>Tasks: {instance.total_tasks_completed}</span>
                        <span>Health: {(instance.health_score * 100).toFixed(0)}%</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AgentSwarmPanel;
