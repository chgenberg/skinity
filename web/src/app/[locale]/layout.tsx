import type {Metadata} from 'next';
import {Geist, Geist_Mono} from 'next/font/google';
import '../globals.css';
import {NextIntlClientProvider} from 'next-intl';
import {setRequestLocale, getMessages} from 'next-intl/server';
import Image from 'next/image';
import Link from 'next/link';

const geistSans = Geist({
  variable: '--font-geist-sans',
  subsets: ['latin']
});

const geistMono = Geist_Mono({
  variable: '--font-geist-mono',
  subsets: ['latin']
});

export const metadata: Metadata = {
  title: 'Skincare Compare',
  description: 'Search and compare skincare products'
};

export function generateStaticParams() {
  return [{locale: 'sv'}, {locale: 'en'}];
}

export default async function LocaleLayout({
  children,
  params: {locale}
}: Readonly<{children: React.ReactNode; params: {locale: string}}>) {
  setRequestLocale(locale);
  const messages = await getMessages();
  return (
    <html lang={locale}>
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased min-h-dvh flex flex-col`}>        
        <header className="sticky top-0 z-30 backdrop-blur-xl/5 supports-[backdrop-filter]:backdrop-blur-xl bg-[color:var(--surface)]/70 border-b border-black/5">
          <div className="container-padded flex h-16 items-center justify-between gap-4">
            <Link href={`/${locale}`} className="flex items-center gap-3">
              <Image src="/skinity_logo.png" alt="Skincare Compare" width={36} height={36} className="rounded-md shadow-sm" />
              <span className="font-semibold tracking-tight">Skincare Compare</span>
            </Link>
            <nav className="flex items-center gap-3 text-sm">
              <Link href={`/${locale}`} className="badge">Home</Link>
              <Link href={`/${locale}`} className="badge">Discover</Link>
              <Link href={`/${locale}`} className="badge">About</Link>
            </nav>
          </div>
        </header>

        <main className="container-padded flex-1 py-8">
          <div className="card p-6 md:p-8">
            <NextIntlClientProvider messages={messages}>{children}</NextIntlClientProvider>
          </div>
        </main>

        <footer className="mt-8 border-t border-black/5">
          <div className="container-padded py-6 text-sm text-[color:var(--muted)]">
            © {new Date().getFullYear()} Skincare Compare
          </div>
        </footer>
      </body>
    </html>
  );
} 