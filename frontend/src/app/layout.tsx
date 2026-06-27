import './globals.css';
import type { Metadata } from 'next';
import { PHProvider } from './providers';

export const metadata: Metadata = {
  title: 'SentiVerse | AI Mood-Based Curation',
  description: 'Describe your current emotion, and SentiVerse curates the perfect media to match your state of mind.',
  metadataBase: new URL('https://sentiverse.ai'), // Replace with your actual domain
  openGraph: {
    title: 'SentiVerse AI',
    description: 'Find media that truly understands your mood.',
    url: 'https://sentiverse.ai',
    siteName: 'SentiVerse',
    images: [
      {
        url: '/og-image.png', // Place this image in your public folder
        width: 1200,
        height: 630,
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'SentiVerse AI',
    description: 'Find media that truly understands your mood.',
  },
};
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-black text-white">
        <PHProvider>
          {children}
        </PHProvider>
      </body>
    </html>
  );
}