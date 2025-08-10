import {getTranslations} from 'next-intl/server';
import SearchBar from '@/components/SearchBar';

export default async function HomePage() {
  const t = await getTranslations('app');
  return (
    <main className="min-h-screen p-6 sm:p-10 space-y-6">
      <div>
        <h1 className="text-2xl font-bold">{t('title')}</h1>
        <p className="text-gray-600">{t('subtitle')}</p>
      </div>
      <SearchBar />
    </main>
  );
} 