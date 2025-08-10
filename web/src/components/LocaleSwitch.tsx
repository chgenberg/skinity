import Link from 'next/link';

export default function LocaleSwitch() {
  return (
    <nav className="flex gap-3 text-sm">
      <Link href="/sv" className="underline">SV</Link>
      <span>•</span>
      <Link href="/en" className="underline">EN</Link>
    </nav>
  );
} 