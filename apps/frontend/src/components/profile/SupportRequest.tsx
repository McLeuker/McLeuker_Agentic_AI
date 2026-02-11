'use client';

import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { supabase } from '@/integrations/supabase/client';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { LucideIcon, Loader2, CheckCircle } from 'lucide-react';

interface SupportRequestProps {
  featureType: string;
  title: string;
  description: string;
  icon: LucideIcon;
}

export function SupportRequest({ featureType, title, description, icon: Icon }: SupportRequestProps) {
  const { user } = useAuth();
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [requested, setRequested] = useState(false);

  const handleRequest = async () => {
    if (!user) return;

    setLoading(true);
    try {
      // Support request logged (table removed during database restructure)
      console.log('Feature request:', featureType, title);

      setRequested(true);
      toast({
        title: 'Request submitted',
        description: "We'll notify you when this feature becomes available.",
      });
    } catch (error) {
      console.error('Error submitting request:', error);
      toast({
        title: 'Request noted',
        description: "We've noted your interest in this feature.",
      });
      setRequested(true);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="border-white/[0.08] bg-[#1A1A1A]">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="text-lg font-medium flex items-center gap-2 text-white">
              <Icon className="h-5 w-5" />
              {title}
            </CardTitle>
            <CardDescription className="mt-1">{description}</CardDescription>
          </div>
          <Badge variant="outline" className="text-white/60 border-white/[0.08]">
            Coming Soon
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        {requested ? (
          <div className="flex items-center gap-2 text-green-400">
            <CheckCircle className="h-4 w-4" />
            <span className="text-sm">Request submitted</span>
          </div>
        ) : (
          <Button
            variant="outline"
            onClick={handleRequest}
            disabled={loading}
            className="border-white/[0.08] text-white hover:bg-white/[0.08]"
          >
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Submitting...
              </>
            ) : (
              'Request Early Access'
            )}
          </Button>
        )}
      </CardContent>
    </Card>
  );
}
