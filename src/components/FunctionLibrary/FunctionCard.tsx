/**
 * Function Card Component
 * 
 * This component displays a single function's documentation in a card format.
 * It includes the function signature, description, parameters, example code,
 * and other relevant information in an organized and readable layout.
 */

import React, { useState } from 'react';
import { FunctionDoc } from '@/types/functions';

interface FunctionCardProps {
  /** Function documentation to display */
  functionDoc: FunctionDoc;
  /** Whether the card is expanded by default */
  defaultExpanded?: boolean;
}

/**
 * Function Card Component
 * 
 * Features:
 * - Collapsible sections for detailed information
 * - Syntax-highlighted code examples
 * - Copy-to-clipboard functionality
 * - Parameter documentation
 * - Tags and metadata display
 */
export default function FunctionCard({ 
  functionDoc, 
  defaultExpanded = false 
}: FunctionCardProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);
  const [copiedSection, setCopiedSection] = useState<string | null>(null);

  /**
   * Copy text to clipboard with feedback
   */
  const copyToClipboard = async (text: string, section: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedSection(section);
      setTimeout(() => setCopiedSection(null), 2000);
    } catch (err) {
      console.error('Failed to copy to clipboard:', err);
    }
  };

  /**
   * Get complexity color class
   */
  const getComplexityColor = (complexity: string) => {
    switch (complexity) {
      case 'Low':
        return 'bg-green-600 text-white';
      case 'Medium':
        return 'bg-yellow-600 text-white';
      case 'High':
        return 'bg-red-600 text-white';
      default:
        return 'bg-gray-600 text-white';
    }
  };

  /**
   * Format parameter type for display
   */
  const formatParameterType = (type: string) => {
    // Simple type formatting - could be enhanced with syntax highlighting
    return type.replace(/\|/g, ' | ').replace(/\[\]/g, '[]');
  };

  return (
    <div className="card-steam p-6">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2">
            <h3 className="text-lg font-semibold text-white truncate">
              {functionDoc.name}
            </h3>
            <span className={`px-2 py-1 text-xs font-medium rounded ${getComplexityColor(functionDoc.complexity)}`}>
              {functionDoc.complexity}
            </span>
          </div>
          
          <p className="text-sm text-gray-300 mb-3">
            {functionDoc.description}
          </p>
          
          <div className="flex items-center gap-2 text-xs text-gray-400">
            <span className="px-2 py-1 bg-steam-blue-light rounded">
              {functionDoc.category}
            </span>
            <span>•</span>
            <span>Updated {functionDoc.lastUpdated}</span>
          </div>
        </div>
        
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="ml-4 p-2 text-gray-400 hover:text-white transition-colors"
          aria-label={isExpanded ? 'Collapse' : 'Expand'}
        >
          <svg 
            className={`w-5 h-5 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>
      </div>

      {/* Tags */}
      <div className="flex flex-wrap gap-1 mb-4">
        {functionDoc.tags.map((tag) => (
          <span
            key={tag}
            className="px-2 py-1 bg-steam-green bg-opacity-20 text-steam-green text-xs rounded"
          >
            #{tag}
          </span>
        ))}
      </div>

      {/* Function Signature */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <h4 className="text-sm font-medium text-white">Signature</h4>
          <button
            onClick={() => copyToClipboard(functionDoc.signature, 'signature')}
            className="text-xs text-gray-400 hover:text-steam-green transition-colors"
          >
            {copiedSection === 'signature' ? 'Copied!' : 'Copy'}
          </button>
        </div>
        <div className="bg-steam-blue-dark p-3 rounded font-mono text-sm text-gray-300 overflow-x-auto">
          {functionDoc.signature}
        </div>
      </div>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="space-y-6">
          {/* Parameters */}
          {functionDoc.parameters.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-white mb-3">Parameters</h4>
              <div className="space-y-3">
                {functionDoc.parameters.map((param) => (
                  <div key={param.name} className="border-l-2 border-steam-green pl-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-mono text-sm text-steam-green">
                            {param.name}
                          </span>
                          <span className="text-xs text-gray-400">
                            {formatParameterType(param.type)}
                          </span>
                          {param.required && (
                            <span className="text-xs text-red-400">required</span>
                          )}
                        </div>
                        <p className="text-sm text-gray-300">
                          {param.description}
                        </p>
                        {param.defaultValue && (
                          <p className="text-xs text-gray-400 mt-1">
                            Default: <code className="font-mono">{param.defaultValue}</code>
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Return Type */}
          <div>
            <h4 className="text-sm font-medium text-white mb-2">Returns</h4>
            <div className="bg-steam-blue-dark p-3 rounded">
              <code className="text-sm text-gray-300">{functionDoc.returnType}</code>
            </div>
          </div>

          {/* Example */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-medium text-white">Example</h4>
              <button
                onClick={() => copyToClipboard(functionDoc.example, 'example')}
                className="text-xs text-gray-400 hover:text-steam-green transition-colors"
              >
                {copiedSection === 'example' ? 'Copied!' : 'Copy Code'}
              </button>
            </div>
            <div className="bg-steam-blue-dark p-4 rounded overflow-x-auto">
              <pre className="text-sm text-gray-300 whitespace-pre-wrap">
                <code>{functionDoc.example}</code>
              </pre>
            </div>
          </div>

          {/* Additional Notes */}
          {functionDoc.notes && (
            <div>
              <h4 className="text-sm font-medium text-white mb-2">Notes</h4>
              <div className="bg-yellow-900 bg-opacity-20 border border-yellow-600 p-3 rounded">
                <p className="text-sm text-yellow-200">{functionDoc.notes}</p>
              </div>
            </div>
          )}

          {/* Related Functions */}
          {functionDoc.relatedFunctions && functionDoc.relatedFunctions.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-white mb-2">Related Functions</h4>
              <div className="flex flex-wrap gap-2">
                {functionDoc.relatedFunctions.map((relatedFunc) => (
                  <span
                    key={relatedFunc}
                    className="px-2 py-1 bg-steam-blue-light text-sm text-gray-300 rounded cursor-pointer hover:bg-steam-blue-light hover:text-white transition-colors"
                  >
                    {relatedFunc}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Source Reference */}
          {functionDoc.sourceFile && (
            <div>
              <h4 className="text-sm font-medium text-white mb-2">Source</h4>
              <div className="text-sm text-gray-400">
                <code>{functionDoc.sourceFile}</code>
                {functionDoc.lineNumber && (
                  <span className="ml-2">Line {functionDoc.lineNumber}</span>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Quick Actions */}
      <div className="mt-4 pt-4 border-t border-steam-blue-light flex items-center justify-between">
        <div className="flex items-center gap-2 text-xs text-gray-400">
          <button
            onClick={() => copyToClipboard(functionDoc.name, 'name')}
            className="hover:text-steam-green transition-colors"
          >
            {copiedSection === 'name' ? 'Copied!' : 'Copy Name'}
          </button>
          <span>•</span>
          <button className="hover:text-steam-green transition-colors">
            Share
          </button>
        </div>
        
        <div className="flex items-center gap-1">
          <button className="p-1 text-gray-400 hover:text-green-400 transition-colors">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
            </svg>
          </button>
          <button className="p-1 text-gray-400 hover:text-red-400 transition-colors">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 13l3 3 7-7" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
