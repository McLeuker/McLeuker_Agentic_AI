/**
 * McLeuker Agentic AI Platform - Task Submitter Component
 * 
 * A component for submitting tasks and viewing generated files.
 * Copy this file into your Lovable project's `src/components/` directory.
 */

import { useState } from 'react';
import { useTask } from '@/hooks/useTask';
import { getFileDownloadUrl } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  Loader2, 
  Play, 
  Download, 
  FileSpreadsheet, 
  FileText, 
  Presentation, 
  Code, 
  Globe,
  CheckCircle,
  XCircle,
  RefreshCw
} from 'lucide-react';

// --- Helper Functions ---

function getFileIcon(format: string) {
  switch (format.toLowerCase()) {
    case 'excel':
    case 'csv':
      return <FileSpreadsheet className="w-5 h-5" />;
    case 'pdf':
    case 'word':
      return <FileText className="w-5 h-5" />;
    case 'ppt':
      return <Presentation className="w-5 h-5" />;
    case 'code':
      return <Code className="w-5 h-5" />;
    case 'web':
    case 'dashboard':
      return <Globe className="w-5 h-5" />;
    default:
      return <FileText className="w-5 h-5" />;
  }
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

// --- Component ---

interface TaskSubmitterProps {
  className?: string;
  title?: string;
  description?: string;
  placeholder?: string;
}

export function TaskSubmitter({
  className = '',
  title = 'Create with AI',
  description = 'Describe what you need, and I\'ll generate the files for you.',
  placeholder = 'Example: Create a competitor analysis for sustainable fashion brands in Europe. Include market share data, key trends, and a summary presentation.',
}: TaskSubmitterProps) {
  const [prompt, setPrompt] = useState('');
  const { task, isLoading, error, progress, submitTask, reset } = useTask();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim() || isLoading) return;
    await submitTask(prompt);
  };

  const handleReset = () => {
    setPrompt('');
    reset();
  };

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Task Form */}
        {!task && (
          <form onSubmit={handleSubmit} className="space-y-4">
            <Textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder={placeholder}
              disabled={isLoading}
              rows={4}
              className="resize-none"
            />

            {/* Progress */}
            {isLoading && (
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>{progress}</span>
                </div>
                <Progress value={33} className="h-2" />
              </div>
            )}

            {/* Error */}
            {error && (
              <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg">
                <XCircle className="w-5 h-5 text-red-500" />
                <p className="text-sm text-red-600">{error.message}</p>
              </div>
            )}

            <Button 
              type="submit" 
              disabled={isLoading || !prompt.trim()}
              className="w-full"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 mr-2" />
                  Generate Files
                </>
              )}
            </Button>
          </form>
        )}

        {/* Task Result */}
        {task && (
          <div className="space-y-4">
            {/* Status */}
            <div className="flex items-center gap-2">
              {task.status === 'completed' ? (
                <>
                  <CheckCircle className="w-5 h-5 text-green-500" />
                  <span className="font-medium text-green-700">Task Completed</span>
                </>
              ) : task.status === 'failed' ? (
                <>
                  <XCircle className="w-5 h-5 text-red-500" />
                  <span className="font-medium text-red-700">Task Failed</span>
                </>
              ) : (
                <>
                  <Loader2 className="w-5 h-5 animate-spin text-blue-500" />
                  <span className="font-medium text-blue-700">Processing...</span>
                </>
              )}
            </div>

            {/* Error Message */}
            {task.error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-600">{task.error}</p>
              </div>
            )}

            {/* Interpretation */}
            {task.interpretation && (
              <div className="p-3 bg-gray-50 border rounded-lg">
                <h4 className="font-medium text-sm text-gray-700 mb-2">
                  Task Understanding
                </h4>
                <p className="text-sm text-gray-600 mb-2">
                  {task.interpretation.intent}
                </p>
                <div className="flex flex-wrap gap-1">
                  <Badge variant="secondary">{task.interpretation.domain}</Badge>
                  {task.interpretation.outputs?.map((output: string, idx: number) => (
                    <Badge key={idx} variant="outline">{output}</Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Generated Files */}
            {task.files && task.files.length > 0 && (
              <div>
                <h4 className="font-medium text-sm text-gray-700 mb-3">
                  Generated Files
                </h4>
                <div className="space-y-2">
                  {task.files.map((file, idx) => (
                    <a
                      key={idx}
                      href={getFileDownloadUrl(file.filename)}
                      download
                      className="flex items-center gap-3 p-3 border rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      <div className="p-2 bg-blue-100 rounded-lg text-blue-600">
                        {getFileIcon(file.format)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-sm truncate">
                          {file.filename}
                        </p>
                        <p className="text-xs text-gray-500">
                          {file.format.toUpperCase()} • {formatFileSize(file.size_bytes)}
                        </p>
                      </div>
                      <Button variant="ghost" size="sm">
                        <Download className="w-4 h-4" />
                      </Button>
                    </a>
                  ))}
                </div>
              </div>
            )}

            {/* New Task Button */}
            <Button 
              onClick={handleReset}
              variant="outline"
              className="w-full"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Create Another Task
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default TaskSubmitter;
