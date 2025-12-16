/**
 * Search Presets Service
 * 
 * Handles saving and loading search configurations (presets).
 * This allows users to save their favorite search combinations and reload them later.
 * 
 * A search preset includes:
 * - Search query text
 * - All active filters (genres, price, type)
 * - Sort order
 * - Preset name and timestamp
 */

export interface SearchPreset {
  name: string;
  timestamp: string;
  query: string;
  filters: {
    genres?: string[];
    price_max?: number;
    type?: string;
    min_reviews?: number;
  };
  sort_by: string;
  description?: string;
}

/**
 * Export current search state as a downloadable JSON file
 * 
 * @param query - Current search query
 * @param filters - Current filter settings
 * @param sortBy - Current sort order
 * @param presetName - Optional name for this preset
 */
export const exportSearchPreset = (
  query: string,
  filters: {
    genres?: string[];
    priceMax?: number;
    gameType?: string;
  },
  sortBy: string,
  presetName?: string
): void => {
  const preset: SearchPreset = {
    name: presetName || `Search Preset ${new Date().toLocaleDateString()}`,
    timestamp: new Date().toISOString(),
    query: query || '',
    filters: {
      genres: filters.genres || [],
      price_max: filters.priceMax ? filters.priceMax * 100 : undefined,
      type: filters.gameType || undefined,
    },
    sort_by: sortBy,
    description: `Search: "${query || 'all games'}" | Genres: ${filters.genres?.join(', ') || 'any'} | Sort: ${sortBy}`
  };

  // Create blob and download
  const blob = new Blob([JSON.stringify(preset, null, 2)], { type: 'application/json' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `search-preset-${Date.now()}.json`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
};

/**
 * Import search preset from a JSON file
 * 
 * @param file - The preset file to import
 * @returns Promise with the parsed preset data
 */
export const importSearchPreset = (file: File): Promise<SearchPreset> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    
    reader.onload = (e) => {
      try {
        const content = e.target?.result as string;
        const preset = JSON.parse(content) as SearchPreset;
        
        // Validate preset structure
        if (!preset.query && preset.query !== '') {
          throw new Error('Invalid preset: missing query field');
        }
        if (!preset.filters) {
          throw new Error('Invalid preset: missing filters field');
        }
        if (!preset.sort_by) {
          throw new Error('Invalid preset: missing sort_by field');
        }
        
        resolve(preset);
      } catch (error) {
        reject(new Error(`Failed to parse preset file: ${error instanceof Error ? error.message : 'Unknown error'}`));
      }
    };
    
    reader.onerror = () => {
      reject(new Error('Failed to read file'));
    };
    
    reader.readAsText(file);
  });
};

/**
 * Save search preset to localStorage for quick access
 * 
 * @param preset - The preset to save
 */
export const savePresetToLocalStorage = (preset: SearchPreset): void => {
  const presets = loadPresetsFromLocalStorage();
  presets.push(preset);
  
  // Keep only last 10 presets
  if (presets.length > 10) {
    presets.shift();
  }
  
  localStorage.setItem('searchPresets', JSON.stringify(presets));
};

/**
 * Load all saved presets from localStorage
 * 
 * @returns Array of saved presets
 */
export const loadPresetsFromLocalStorage = (): SearchPreset[] => {
  try {
    const stored = localStorage.getItem('searchPresets');
    return stored ? JSON.parse(stored) : [];
  } catch {
    return [];
  }
};

/**
 * Delete a preset from localStorage
 * 
 * @param timestamp - Timestamp of the preset to delete
 */
export const deletePresetFromLocalStorage = (timestamp: string): void => {
  const presets = loadPresetsFromLocalStorage();
  const filtered = presets.filter(p => p.timestamp !== timestamp);
  localStorage.setItem('searchPresets', JSON.stringify(filtered));
};

/**
 * Clear all saved presets from localStorage
 */
export const clearAllPresets = (): void => {
  localStorage.removeItem('searchPresets');
};


