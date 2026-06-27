export const ShareButton = ({ mood }: { mood: string }) => {
  const handleShare = () => {
    const url = `${window.location.origin}/?mood=${encodeURIComponent(mood)}`;
    navigator.clipboard.writeText(url);
    alert('Mood search copied to clipboard!');
  };

  return (
    <button onClick={handleShare} className="text-sm text-indigo-400 hover:text-indigo-300">
      Share this mood
    </button>
  );
};