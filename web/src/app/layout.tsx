import type {Metadata} from 'next';

export const metadata: Metadata = {
  title: 'Skincare Compare',
  description: 'Search and compare skincare products'
};

export default function RootLayout({children}: Readonly<{children: React.ReactNode}>) {
  return (
    <html lang="sv">
      <body>{children}</body>
    </html>
  );
}
