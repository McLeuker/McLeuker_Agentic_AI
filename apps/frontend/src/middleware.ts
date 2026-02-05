import { createServerClient } from '@supabase/ssr';
import { NextResponse, type NextRequest } from 'next/server';

export async function middleware(request: NextRequest) {
  let supabaseResponse = NextResponse.next({
    request,
  });

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll();
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value }) =>
            request.cookies.set(name, value)
          );
          supabaseResponse = NextResponse.next({
            request,
          });
          cookiesToSet.forEach(({ name, value, options }) =>
            supabaseResponse.cookies.set(name, value, {
              ...options,
              // Ensure cookies persist properly
              maxAge: options?.maxAge ?? 60 * 60 * 24 * 365, // 1 year default
              sameSite: 'lax',
              secure: process.env.NODE_ENV === 'production',
              path: '/',
            })
          );
        },
      },
    }
  );

  // IMPORTANT: Avoid writing any logic between createServerClient and
  // supabase.auth.getUser(). A simple mistake could make it very hard to debug
  // issues with users being randomly logged out.

  // Get user - this also refreshes the session if needed
  const {
    data: { user },
    error,
  } = await supabase.auth.getUser();

  // Log auth errors for debugging (but don't fail)
  if (error) {
    console.log('Middleware auth check:', error.message);
  }

  // Protected routes - redirect to login if not authenticated
  const protectedPaths = ['/dashboard', '/settings', '/billing', '/preferences', '/profile'];
  const isProtectedPath = protectedPaths.some(path => 
    request.nextUrl.pathname.startsWith(path)
  );

  // Public paths that should never redirect
  const publicPaths = ['/', '/login', '/signup', '/auth', '/api', '/_next', '/favicon'];
  const isPublicPath = publicPaths.some(path => 
    request.nextUrl.pathname.startsWith(path) || request.nextUrl.pathname === path
  );

  if (isProtectedPath && !user) {
    // Store the intended destination for redirect after login
    const url = request.nextUrl.clone();
    const redirectTo = request.nextUrl.pathname + request.nextUrl.search;
    url.pathname = '/login';
    url.searchParams.set('redirectTo', redirectTo);
    return NextResponse.redirect(url);
  }

  // Redirect logged-in users away from login/signup pages
  if ((request.nextUrl.pathname === '/login' || request.nextUrl.pathname === '/signup') && user) {
    const url = request.nextUrl.clone();
    // Check if there's a redirectTo parameter
    const redirectTo = request.nextUrl.searchParams.get('redirectTo');
    url.pathname = redirectTo || '/dashboard';
    url.search = '';
    return NextResponse.redirect(url);
  }

  // IMPORTANT: You *must* return the supabaseResponse object as it is. If you're
  // creating a new response object with NextResponse.next() make sure to:
  // 1. Pass the request in it, like so:
  //    const myNewResponse = NextResponse.next({ request })
  // 2. Copy over the cookies, like so:
  //    myNewResponse.cookies.setAll(supabaseResponse.cookies.getAll())
  // 3. Change the myNewResponse object to fit your needs, but avoid changing
  //    the cookies!
  // 4. Finally:
  //    return myNewResponse
  // If this is not done, you may be causing the browser and server to go out
  // of sync and terminate the user's session prematurely!

  return supabaseResponse;
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     * - api routes (handled separately)
     */
    '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp|ico)$).*)',
  ],
};
