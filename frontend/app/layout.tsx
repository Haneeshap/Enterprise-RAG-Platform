import './globals.css';

export const metadata = {
  title: 'Enterprise RAG Platform',
  description: 'AI-Powered Retrieval-Augmented Generation Platform',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}