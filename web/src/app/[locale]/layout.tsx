import type {Metadata} from 'next';
import {Geist, Geist_Mono} from 'next/font/google';
import '../globals.css';
import {NextIntlClientProvider} from 'next-intl';
import {setRequestLocale, getMessages} from 'next-intl/server';
import LocaleSwitch from '@/components/LocaleSwitch';

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
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        <div className="p-4 border-b flex items-center justify-between">
          <div className="font-semibold">Skincare Compare</div>
          <LocaleSwitch />
        </div>
        <NextIntlClientProvider messages={messages}>{children}</NextIntlClientProvider>
      </body>
    </html>
  );
} 