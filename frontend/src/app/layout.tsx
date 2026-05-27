'use client';

import "./globals.css";
// Amplify設定をインポートするだけで自動的に設定される
import "@/lib/amplify-config";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ja">
      <head>
        <title>EleKnowledge-AI</title>
        <meta name="description" content="AI-powered knowledge management system for electrical equipment" />
      </head>
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
