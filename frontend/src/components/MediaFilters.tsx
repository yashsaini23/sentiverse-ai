import React from 'react';

const MEDIA_TYPES = ['All', 'Movie', 'Anime', 'Game', 'Novel', 'Podcast'];

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
      onChange(selectedFilters.filter(f => f !== type));
    } else {
      onChange([...selectedFilters, type]);
    }
  };

  const isAllSelected = selectedFilters.length === 0;

  return (
    <div className="flex flex-wrap justify-center gap-3 mb-6">
      {MEDIA_TYPES.map((type) => {
        const isSelected = type === 'All' ? isAllSelected : selectedFilters.includes(type);
        return (
          <button
            key={type}
            type="button"
            onClick={() => toggleFilter(type)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium transition-all duration-200 border ${
              isSelected 
                ? 'bg-indigo-500/20 text-indigo-300 border-indigo-500/50 shadow-[0_0_15px_rgba(99,102,241,0.2)]' 
                : 'bg-white/5 text-gray-400 border-white/5 hover:bg-white/10 hover:text-gray-300'
            }`}
          >
            {type}
          </button>
        );
      })}
    </div>
  );
};