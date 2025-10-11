/**
 * Function Documentation Types
 * 
 * This file contains TypeScript type definitions for the function library
 * documentation system. These types ensure consistent structure for
 * documenting all functions in the Steam Game Search Engine project.
 */

/**
 * Function parameter documentation
 */
export interface FunctionParameter {
  /** Parameter name */
  name: string;
  /** Parameter type (TypeScript type) */
  type: string;
  /** Parameter description */
  description: string;
  /** Whether the parameter is required */
  required: boolean;
  /** Default value if parameter is optional */
  defaultValue?: string;
  /** Example values for the parameter */
  examples?: string[];
}

/**
 * Function complexity levels
 */
export type FunctionComplexity = 'Low' | 'Medium' | 'High';

/**
 * Function categories for organization
 */
export type FunctionCategory =
  | 'API Client'
  | 'API Endpoint'
  | 'Search Algorithm'
  | 'Data Processing'
  | 'Data Access'
  | 'Validation'
  | 'Utility'
  | 'UI Components'
  | 'Hooks'
  | 'Services';

/**
 * Complete function documentation structure
 */
export interface FunctionDoc {
  /** Unique identifier for the function */
  id: string;
  /** Function name */
  name: string;
  /** Category for organization */
  category: FunctionCategory;
  /** Brief description of what the function does */
  description: string;
  /** Full function signature with types */
  signature: string;
  /** Array of function parameters */
  parameters: FunctionParameter[];
  /** Return type description */
  returnType: string;
  /** Code example showing usage */
  example: string;
  /** Tags for searching and filtering */
  tags: string[];
  /** Complexity level */
  complexity: FunctionComplexity;
  /** Last update date */
  lastUpdated: string;
  /** Optional additional notes */
  notes?: string;
  /** Related functions */
  relatedFunctions?: string[];
  /** Source file path */
  sourceFile?: string;
  /** Line number in source file */
  lineNumber?: number;
}

/**
 * Function search and filter options
 */
export interface FunctionSearchOptions {
  /** Search query text */
  query?: string;
  /** Filter by category */
  category?: FunctionCategory | 'all';
  /** Filter by complexity */
  complexity?: FunctionComplexity[];
  /** Filter by tags */
  tags?: string[];
  /** Sort order */
  sortBy?: 'name' | 'category' | 'complexity' | 'lastUpdated';
  /** Sort direction */
  sortDirection?: 'asc' | 'desc';
}

/**
 * Function library statistics
 */
export interface FunctionLibraryStats {
  /** Total number of functions */
  totalFunctions: number;
  /** Number of categories */
  totalCategories: number;
  /** Functions by complexity */
  complexityBreakdown: Record<FunctionComplexity, number>;
  /** Functions by category */
  categoryBreakdown: Record<FunctionCategory, number>;
  /** Most recent update date */
  lastUpdated: string;
  /** Documentation coverage percentage */
  coveragePercentage: number;
}

/**
 * Markdown parsing result
 */
export interface MarkdownParseResult {
  /** Successfully parsed functions */
  functions: FunctionDoc[];
  /** Parsing errors */
  errors: string[];
  /** Warnings during parsing */
  warnings: string[];
  /** Source file metadata */
  metadata: {
    filePath: string;
    lastModified: string;
    size: number;
  };
}

/**
 * Export format options
 */
export type ExportFormat = 'pdf' | 'markdown' | 'json' | 'html';

/**
 * Export configuration
 */
export interface ExportConfig {
  /** Export format */
  format: ExportFormat;
  /** Functions to include (empty array = all) */
  includeFunctions?: string[];
  /** Categories to include */
  includeCategories?: FunctionCategory[];
  /** Whether to include examples */
  includeExamples: boolean;
  /** Whether to include source references */
  includeSourceRefs: boolean;
  /** Custom styling options */
  styling?: {
    theme?: 'light' | 'dark' | 'steam';
    fontSize?: number;
    includeTableOfContents?: boolean;
  };
}

/**
 * Validation result for function documentation
 */
export interface ValidationResult {
  /** Whether the documentation is valid */
  isValid: boolean;
  /** Validation errors */
  errors: string[];
  /** Validation warnings */
  warnings: string[];
  /** Suggestions for improvement */
  suggestions: string[];
}

/**
 * Function usage analytics
 */
export interface FunctionUsageAnalytics {
  /** Function ID */
  functionId: string;
  /** Number of times viewed */
  viewCount: number;
  /** Number of times copied */
  copyCount: number;
  /** Average time spent viewing */
  averageViewTime: number;
  /** Most common search terms leading to this function */
  searchTerms: string[];
  /** User feedback ratings */
  ratings: {
    helpful: number;
    notHelpful: number;
    averageRating: number;
  };
}
