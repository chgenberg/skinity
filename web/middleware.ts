import createIntlMiddleware from 'next-intl/middleware';
import {NextRequest} from 'next/server';

export default function middleware(request: NextRequest) {
  const handleI18nRouting = createIntlMiddleware({
    locales: ['sv', 'en'],
    defaultLocale: 'sv'
  });
  return handleI18nRouting(request);
}

export const config = {
  matcher: ['/((?!_next|.*\..*).*)']
}; 