// React explainability widget with real-time reasoning tree streaming
'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ThumbsUp, ThumbsDown, ChevronDown, ChevronRight } from 'lucide-react';

interface RetrievedDoc {
  id: string;
  content: string;
  relevance_score: number;
  metadata: {
    source: string;
    score: number;
  };
}

interface ReasoningStep {
  step: string;
  content: any;
  timestamp: number;
  confidence?: number;
}

interface ExplainabilityData {
  retrieved_docs: RetrievedDoc[];
  reasoning_tree: ReasoningStep[];
  explainability_score: number;
}

interface ExplainProps {
  query: string;
  onFeedback?: (feedback: 'positive' | 'negative', context: any) => void;
}

export function ExplainWidget({ query, onFeedback }: ExplainProps) {
  const [data, setData] = useState<ExplainabilityData | null>(null);
  const [loading, setLoading] = useState(false);
  const [expandedDocs, setExpandedDocs] = useState<Set<string>>(new Set());
  const [expandedSteps, setExpandedSteps] = useState<Set<string>>(new Set());
  const [streamingSteps, setStreamingSteps] = useState<ReasoningStep[]>([]);

  // NOVEL: Real-time streaming of reasoning process
  useEffect(() => {
    if (!query) return;

    const fetchExplanation = async () => {
      setLoading(true);
      setStreamingSteps([]);

      try {
        // Start with basic explanation
        const response = await fetch('/explain', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            query, 
            include_reasoning: true 
          }),
        });

        const explanation = await response.json();
        setData(explanation);

        // NOVEL: Stream reasoning process in real-time
        const streamResponse = await fetch('/chat-tot', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            message: `Explain reasoning for: ${query}`,
            context: { explanation_mode: true }
          }),
        });

        if (streamResponse.body) {
          const reader = streamResponse.body.getReader();
          const decoder = new TextDecoder();

          while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            const lines = chunk.split('\n').filter(line => line.startsWith('data: '));

            for (const line of lines) {
              try {
                const data = JSON.parse(line.slice(6));
                if (data.type === 'reasoning_step') {
                  setStreamingSteps(prev => [...prev, data.content]);
                }
              } catch (e) {
                console.warn('Failed to parse streaming data:', e);
              }
            }
          }
        }
      } catch (error) {
        console.error('Failed to fetch explanation:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchExplanation();
  }, [query]);

  const toggleDocExpansion = (docId: string) => {
    setExpandedDocs(prev => {
      const next = new Set(prev);
      if (next.has(docId)) {
        next.delete(docId);
      } else {
        next.add(docId);
      }
      return next;
    });
  };

  const toggleStepExpansion = (stepId: string) => {
    setExpandedSteps(prev => {
      const next = new Set(prev);
      if (next.has(stepId)) {
        next.delete(stepId);
      } else {
        next.add(stepId);
      }
      return next;
    });
  };

  const handleFeedback = (type: 'positive' | 'negative') => {
    // NOVEL: Contextual feedback collection for improvement
    const feedbackContext = {
      query,
      explainability_score: data?.explainability_score,
      reasoning_steps: streamingSteps.length,
      retrieved_docs_count: data?.retrieved_docs.length || 0,
      timestamp: Date.now()
    };

    onFeedback?.(type, feedbackContext);
  };

  if (loading && !data) {
    return (
      <Card className="w-full max-w-4xl mx-auto">
        <CardContent className="p-6">
          <div className="animate-pulse space-y-4">
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            <div className="h-4 bg-gray-200 rounded w-2/3"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="w-full max-w-6xl mx-auto space-y-6">
      {/* Explainability Score Header */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Reasoning Explanation</span>
            <div className="flex items-center space-x-4">
              <Badge variant={
                (data?.explainability_score || 0) > 0.8 ? 'default' :
                (data?.explainability_score || 0) > 0.6 ? 'secondary' : 'destructive'
              }>
                Explainability: {((data?.explainability_score || 0) * 100).toFixed(1)}%
              </Badge>
              <div className="flex space-x-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleFeedback('positive')}
                >
                  <ThumbsUp className="h-4 w-4" />
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleFeedback('negative')}
                >
                  <ThumbsDown className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </CardTitle>
        </CardHeader>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Retrieved Documents */}
        <Card>
          <CardHeader>
            <CardTitle>Retrieved Knowledge ({data?.retrieved_docs.length || 0})</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {data?.retrieved_docs.map((doc) => (
              <div key={doc.id} className="border rounded-lg p-4">
                <div 
                  className="flex items-center justify-between cursor-pointer"
                  onClick={() => toggleDocExpansion(doc.id)}
                >
                  <div className="flex items-center space-x-2">
                    {expandedDocs.has(doc.id) ? 
                      <ChevronDown className="h-4 w-4" /> : 
                      <ChevronRight className="h-4 w-4" />
                    }
                    <span className="font-medium">{doc.metadata.source}</span>
                  </div>
                  <Badge variant="secondary">
                    {(doc.relevance_score * 100).toFixed(1)}%
                  </Badge>
                </div>
                
                {expandedDocs.has(doc.id) && (
                  <div className="mt-3 text-sm text-gray-600">
                    <p>{doc.content}</p>
                  </div>
                )}
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Reasoning Tree */}
        <Card>
          <CardHeader>
            <CardTitle>
              Reasoning Process 
              {streamingSteps.length > 0 && (
                <Badge className="ml-2" variant="outline">
                  {streamingSteps.length} steps
                </Badge>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Static reasoning tree */}
            {data?.reasoning_tree.map((step, index) => (
              <div key={`static-${index}`} className="border rounded-lg p-4">
                <div 
                  className="flex items-center justify-between cursor-pointer"
                  onClick={() => toggleStepExpansion(`static-${index}`)}
                >
                  <div className="flex items-center space-x-2">
                    {expandedSteps.has(`static-${index}`) ? 
                      <ChevronDown className="h-4 w-4" /> : 
                      <ChevronRight className="h-4 w-4" />
                    }
                    <span className="font-medium capitalize">
                      {step.step.replace('_', ' ')}
                    </span>
                  </div>
                  {step.confidence && (
                    <Badge variant="secondary">
                      {(step.confidence * 100).toFixed(1)}%
                    </Badge>
                  )}
                </div>
                
                {expandedSteps.has(`static-${index}`) && (
                  <div className="mt-3 text-sm">
                    <pre className="bg-gray-50 p-2 rounded text-xs overflow-x-auto">
                      {JSON.stringify(step.content, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            ))}

            {/* NOVEL: Real-time streaming reasoning steps */}
            {streamingSteps.map((step, index) => (
              <div 
                key={`stream-${index}`} 
                className="border rounded-lg p-4 bg-blue-50 border-blue-200"
              >
                <div 
                  className="flex items-center justify-between cursor-pointer"
                  onClick={() => toggleStepExpansion(`stream-${index}`)}
                >
                  <div className="flex items-center space-x-2">
                    {expandedSteps.has(`stream-${index}`) ? 
                      <ChevronDown className="h-4 w-4" /> : 
                      <ChevronRight className="h-4 w-4" />
                    }
                    <span className="font-medium">
                      Live: {step.step || 'Processing...'}
                    </span>
                  </div>
                  <Badge variant="default">Real-time</Badge>
                </div>
                
                {expandedSteps.has(`stream-${index}`) && (
                  <div className="mt-3 text-sm">
                    <pre className="bg-white p-2 rounded text-xs overflow-x-auto border">
                      {JSON.stringify(step.content, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            ))}

            {loading && streamingSteps.length === 0 && (
              <div className="flex items-center space-x-2 text-gray-500">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
                <span>Generating reasoning steps...</span>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default ExplainWidget;
