/**
 * Next.js Document Component
 * 
 * This component customizes the HTML document structure for the Steam Game Search Engine.
 * It's used to augment the application's <html> and <body> tags and is only rendered on the server.
 */

import React from 'react';
import { Html, Head, Main, NextScript } from 'next/document';

/**
 * Custom Document Component
 * 
 * Features:
 * - Custom HTML structure
 * - Language and accessibility attributes
 * - Performance optimizations
 * - SEO enhancements
 */
export default function Document() {
  return (
    <Html lang="en" className="h-full">
      <Head>
        {/* Performance optimizations */}
        <link rel="dns-prefetch" href="//fonts.googleapis.com" />
        <link rel="dns-prefetch" href="//fonts.gstatic.com" />
        
        {/* Preload critical resources */}
        <link
          rel="preload"
          href="/fonts/inter-var.woff2"
          as="font"
          type="font/woff2"
          crossOrigin="anonymous"
        />
        
        {/* Critical CSS for above-the-fold content */}
        <style
          dangerouslySetInnerHTML={{
            __html: `
              /* Critical CSS for initial page load */
              body {
                background-color: #171a21;
                color: #ffffff;
                font-family: Arial, Helvetica, sans-serif;
              }
              
              /* Loading state styles */
              .loading-skeleton {
                background: linear-gradient(90deg, #2a475e 25%, #1b2838 50%, #2a475e 75%);
                background-size: 200% 100%;
                animation: loading 1.5s infinite;
              }
              
              @keyframes loading {
                0% { background-position: 200% 0; }
                100% { background-position: -200% 0; }
              }
              
              /* Prevent flash of unstyled content */
              .no-js {
                display: none;
              }
            `,
          }}
        />
      </Head>
      
      <body className="h-full bg-steam-blue-dark text-white antialiased">
        {/* No-JavaScript fallback */}
        <noscript>
          <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: '#171a21',
            color: '#ffffff',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexDirection: 'column',
            zIndex: 9999,
            textAlign: 'center',
            padding: '20px'
          }}>
            <h1 style={{ fontSize: '24px', marginBottom: '16px' }}>
              JavaScript Required
            </h1>
            <p style={{ fontSize: '16px', marginBottom: '16px' }}>
              Steam Game Search Engine requires JavaScript to function properly.
            </p>
            <p style={{ fontSize: '14px', color: '#999' }}>
              Please enable JavaScript in your browser and refresh the page.
            </p>
          </div>
        </noscript>

        {/* Main application content */}
        <Main />
        
        {/* Next.js scripts */}
        <NextScript />
        
        {/* Analytics and tracking scripts */}
        {process.env.NODE_ENV === 'production' && (
          <>
            {/* Google Analytics */}
            {process.env.NEXT_PUBLIC_GA_ID && (
              <>
                <script
                  async
                  src={`https://www.googletagmanager.com/gtag/js?id=${process.env.NEXT_PUBLIC_GA_ID}`}
                />
                <script
                  dangerouslySetInnerHTML={{
                    __html: `
                      window.dataLayer = window.dataLayer || [];
                      function gtag(){dataLayer.push(arguments);}
                      gtag('js', new Date());
                      gtag('config', '${process.env.NEXT_PUBLIC_GA_ID}', {
                        page_title: document.title,
                        page_location: window.location.href,
                      });
                    `,
                  }}
                />
              </>
            )}
            
            {/* Performance monitoring */}
            <script
              dangerouslySetInnerHTML={{
                __html: `
                  // Basic performance monitoring
                  window.addEventListener('load', function() {
                    if ('performance' in window) {
                      const perfData = performance.getEntriesByType('navigation')[0];
                      if (perfData) {
                        console.log('Page load time:', perfData.loadEventEnd - perfData.fetchStart, 'ms');
                      }
                    }
                  });
                `,
              }}
            />
          </>
        )}
        
        {/* Development helpers */}
        {process.env.NODE_ENV === 'development' && (
          <script
            dangerouslySetInnerHTML={{
              __html: `
                // Development mode indicators
                document.body.setAttribute('data-env', 'development');
                
                // Console styling for development
                const styles = {
                  title: 'color: #90ba3c; font-size: 20px; font-weight: bold;',
                  subtitle: 'color: #66c0f4; font-size: 14px;',
                  info: 'color: #999; font-size: 12px;'
                };
                
                console.log('%c🎮 Steam Game Search Engine', styles.title);
                console.log('%cDevelopment Build', styles.subtitle);
                console.log('%cINST326 Group Project - University of Maryland', styles.info);
                
                // Hot reload notification
                if (module.hot) {
                  console.log('%c🔥 Hot reload enabled', 'color: #ff6600; font-size: 12px;');
                }
              `,
            }}
          />
        )}
      </body>
    </Html>
  );
}
