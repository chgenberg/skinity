"use client";

import {useState, useMemo} from 'react';
import useSWR from 'swr';
import {fetcher} from '@/lib/api';
import {useTranslations} from 'next-intl';

function buildQuery(params: Record<string, string | number | undefined>) {
  const usp = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== '') usp.append(k, String(v));
  });
  const qs = usp.toString();
  return `/search${qs ? `?${qs}` : ''}`;
}

function getHost(url?: string): string | null {
  try {
    if (!url) return null;
    const u = new URL(url);
    return u.host;
  } catch {
    return null;
  }
}

export default function SearchBar() {
  const t = useTranslations();
  const [q, setQ] = useState('');
  const [minPrice, setMinPrice] = useState<string>('');
  const [maxPrice, setMaxPrice] = useState<string>('');
  const [tag, setTag] = useState('');
  const [skinType, setSkinType] = useState('');
  const [ingredient, setIngredient] = useState('');

  const key = useMemo(
    () =>
      buildQuery({
        q,
        min_price: minPrice ? Number(minPrice) : undefined,
        max_price: maxPrice ? Number(maxPrice) : undefined,
        tag: tag || undefined,
        skin_type: skinType || undefined,
        ingredient: ingredient || undefined,
        limit: 50,
      }),
    [q, minPrice, maxPrice, tag, skinType, ingredient]
  );

  const {data, isLoading} = useSWR(key, fetcher, {revalidateOnFocus: false});

  function clearFilters() {
    setQ('');
    setMinPrice('');
    setMaxPrice('');
    setTag('');
    setSkinType('');
    setIngredient('');
  }

  return (
    <div className="w-full space-y-6">
      <div className="flex items-center justify-between">
        <div className="text-sm text-[color:var(--muted)]">{t('results.providers')} & {t('results.products')}</div>
        <button className="button-ghost" onClick={clearFilters}>Rensa filter</button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-6 gap-3">
        <input
          className="input md:col-span-2"
          placeholder={t('search.placeholder')}
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
        <input
          className="input"
          placeholder={t('search.minPrice')}
          inputMode="decimal"
          value={minPrice}
          onChange={(e) => setMinPrice(e.target.value)}
        />
        <input
          className="input"
          placeholder={t('search.maxPrice')}
          inputMode="decimal"
          value={maxPrice}
          onChange={(e) => setMaxPrice(e.target.value)}
        />
        <input
          className="input"
          placeholder={t('search.tag')}
          value={tag}
          onChange={(e) => setTag(e.target.value)}
        />
        <input
          className="input"
          placeholder={t('search.ingredient')}
          value={ingredient}
          onChange={(e) => setIngredient(e.target.value)}
        />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
        <input
          className="input"
          placeholder={t('search.skinType')}
          value={skinType}
          onChange={(e) => setSkinType(e.target.value)}
        />
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        <div className="card hoverable p-4">
          <h3 className="font-semibold mb-2">{t('results.providers')}</h3>
          {isLoading ? (
            <p>Loading...</p>
          ) : data?.providers?.length ? (
            <ul className="divide-y">
              {data.providers.map((p: any) => (
                <li key={`prov-${p.id}`} className="py-2">
                  <div className="font-medium">{p.name}</div>
                  {p.website ? (
                    <a className="text-[color:var(--primary)] underline" href={p.website} target="_blank" rel="noreferrer">
                      {p.website}
                    </a>
                  ) : null}
                  {p.country ? <div className="text-sm text-[color:var(--muted)]">{p.country}</div> : null}
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-[color:var(--muted)]">{t('results.empty')}</p>
          )}
        </div>
        <div className="card hoverable p-4">
          <h3 className="font-semibold mb-2">{t('results.products')}</h3>
          {isLoading ? (
            <p>Loading...</p>
          ) : data?.products?.length ? (
            <ul className="divide-y">
              {data.products.map((p: any) => {
                const host = getHost(p.url || undefined);
                return (
                  <li key={`prod-${p.id}`} className="py-3">
                    <div className="flex items-baseline justify-between gap-3">
                      <div className="font-medium">{p.name}</div>
                      {p.price_amount != null ? (
                        <div className="text-sm whitespace-nowrap">{p.price_amount} {p.price_currency}</div>
                      ) : null}
                    </div>
                    {host ? <div className="text-xs text-[color:var(--muted)]">{host}</div> : null}
                    {p.url ? (
                      <a className="text-[color:var(--primary)] underline break-all" href={p.url} target="_blank" rel="noreferrer">
                        {p.url}
                      </a>
                    ) : null}
                    {Array.isArray(p.inci) && p.inci.length ? (
                      <div className="mt-2 flex flex-wrap gap-1">
                        {p.inci.slice(0, 12).map((ing: string, idx: number) => (
                          <span key={`${p.id}-ing-${idx}`} className="badge">{ing}</span>
                        ))}
                        {p.inci.length > 12 ? (
                          <span className="badge">+{p.inci.length - 12}</span>
                        ) : null}
                      </div>
                    ) : null}
                  </li>
                );
              })}
            </ul>
          ) : (
            <p className="text-sm text-[color:var(--muted)]">{t('results.empty')}</p>
          )}
        </div>
      </div>
    </div>
  );
} 