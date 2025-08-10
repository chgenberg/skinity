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
        {/* Top marquee banner */}
        <div className="banner-marquee">
          <div className="container-padded h-full flex items-center">
            <span className="banner-track text-sm">
              Hitta och jämför hudvård helt gratis • Find and compare skincare for free • Hitta och jämför hudvård helt gratis • Find and compare skincare for free
            </span>
          </div>
        </div>

        {/* Header under banner, offset via sticky top equal to banner height */}
        <header className="sticky top-[var(--banner-h)] z-30 backdrop-blur-xl/5 supports-[backdrop-filter]:backdrop-blur-xl bg-[color:var(--surface)]/70 border-b border-black/5">
          <div className="container-padded grid grid-cols-3 h-20 items-center">
            <div />
            <div className="flex items-center justify-center">
              <Link href={`/${locale}`} className="flex items-center gap-4 hover-scale">
                <Image src="/skinity_logo.png" alt="Skincare Compare" width={64} height={64} className="rounded-xl shadow-sm" />
                <span className="sr-only">Skincare Compare</span>
              </Link>
            </div>
            <nav className="flex items-center justify-end gap-3 text-sm">
              <Link href={`/${locale}`} className="badge">Home</Link>
              <Link href={`/${locale}`} className="badge">Discover</Link>
              <Link href={`/${locale}`} className="badge">About</Link>
            </nav>
          </div>
        </header>

        {/* Hero */}
        <section className="container-padded pt-8">
          <div className="card hoverable p-8 md:p-10 text-center">
            <h1 className="text-3xl md:text-4xl font-semibold tracking-tight mb-2 text-gradient">Jämför hudvård – smartare, snabbare</h1>
            <p className="text-[color:var(--muted)] max-w-2xl mx-auto">Sök, filtrera och hitta rätt produkter och varumärken baserat på pris, ingredienser och hudtyp.</p>
          </div>
        </section>

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