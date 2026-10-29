import React from 'react';

// TMDB currently powers these two media types. Additional providers can be added
// without showing filters that cannot return results yet.
const MEDIA_TYPES = ['All', 'Movie', 'TV'];

interface MediaFiltersProps {
  selectedFilters: string[];
  onChange: (filters: string[]) => void;
}

export const MediaFilters: React.FC<MediaFiltersProps> = ({ selectedFilters, onChange }) => {
  const toggleFilter = (type: string) => {
    if (type === 'All') {
      onChange([]);
      return;
    }

    if (selectedFilters.includes(type)) {
      onChange(selectedFilters.filter((filter) => filter !== type));
    } else {
      onChange([...selectedFilters, type]);
    }
  };

  const isAllSelected = selectedFilters.length === 0;

  return (
    <div className="mb-6 flex flex-wrap justify-center gap-3">
      {MEDIA_TYPES.map((type) => {
        const isSelected = type === 'All' ? isAllSelected : selectedFilters.includes(type);
        return (
          <button
            key={type}
            type="button"
            onClick={() => toggleFilter(type)}
            aria-pressed={isSelected}
            className={`rounded-full border px-4 py-1.5 text-sm font-medium transition-all duration-200 ${
              isSelected
                ? 'border-indigo-500/50 bg-indigo-500/20 text-indigo-300 shadow-[0_0_15px_rgba(99,102,241,0.2)]'
                : 'border-white/5 bg-white/5 text-gray-400 hover:bg-white/10 hover:text-gray-300'
            }`}
          >
            {type}
          </button>
        );
      })}
    </div>
  );
};
