import { createServerClient } from '@supabase/ssr';
import { NextResponse, type NextRequest } from 'next/server';

export async function middleware(request: NextRequest) {
  // Create a response object that we can modify
  let response = NextResponse.next({
    request,
  });

  // Create Supabase client with proper cookie handling
  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll();
        },
        setAll(cookiesToSet) {
          // First, set cookies on the request (for downstream handlers)
          cookiesToSet.forEach(({ name, value }) =>
            request.cookies.set(name, value)
          );
          
          // Create a new response with the updated request
          response = NextResponse.next({
            request,
          });
          
          // Then, set cookies on the response (for the browser)
          cookiesToSet.forEach(({ name, value, options }) =>
            response.cookies.set(name, value, {
              ...options,
              // Ensure consistent cookie settings across the app
              sameSite: 'lax',
              secure: process.env.NODE_ENV === 'production',
              path: '/',
              // Default to 1 year expiry for session persistence
              maxAge: options?.maxAge ?? 60 * 60 * 24 * 365,
            })
          );
        },
      },
    }
  );

  // IMPORTANT: Do not add any logic between createServerClient and getUser()
  // This could cause session sync issues

  // Refresh session if needed - this is critical for maintaining auth state
  const { data: { user }, error } = await supabase.auth.getUser();

  // Log errors for debugging but don't fail the request
  if (error && error.message !== 'Auth session missing!') {
    console.log('Middleware auth error:', error.message);
  }

  // Define protected and public paths
  const protectedPaths = ['/dashboard', '/settings', '/billing', '/preferences', '/profile'];
  const authPaths = ['/login', '/signup'];
  const publicPaths = ['/', '/about', '/solutions', '/pricing', '/contact', '/auth', '/api', '/_next', '/favicon', '/terms', '/privacy', '/cookies'];

  const pathname = request.nextUrl.pathname;
  
  const isProtectedPath = protectedPaths.some(path => pathname.startsWith(path));
  const isAuthPath = authPaths.some(path => pathname === path);
  const isPublicPath = publicPaths.some(path => pathname.startsWith(path) || pathname === path);

  // Redirect unauthenticated users from protected paths to login
  if (isProtectedPath && !user) {
    const url = request.nextUrl.clone();
    const redirectTo = pathname + request.nextUrl.search;
    url.pathname = '/login';
    url.searchParams.set('redirectTo', redirectTo);
    return NextResponse.redirect(url);
  }

  // Redirect authenticated users away from auth pages to dashboard
  if (isAuthPath && user) {
    const url = request.nextUrl.clone();
    const redirectTo = request.nextUrl.searchParams.get('redirectTo');
    url.pathname = redirectTo || '/dashboard';
    url.search = '';
    return NextResponse.redirect(url);
  }

  // IMPORTANT: Always return the response object with cookies
  return response;
}

export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - Static assets (images, fonts, etc.)
     */
    '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp|ico|woff|woff2|ttf|eot)$).*)',
  ],
};
