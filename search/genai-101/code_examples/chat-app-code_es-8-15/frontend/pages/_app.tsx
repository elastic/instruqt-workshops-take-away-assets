// pages/_app.tsx
import '../src/app/globals.css'; // Ensure this path is correct


// pages/_app.tsx
import { Inter } from 'next/font/google';
import '../src/app/globals.css'; // Ensure your global styles are also imported if they are not already

// Import Inter font with specific styles
const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  weights: ['400', '700'] // Specify the weights you need
});

export default function MyApp({ Component, pageProps }) {
  return (
    <>
      <style jsx global>{`
        body {
          font-family: ${inter.variable}, sans-serif;
        }
      `}</style>
      <Component {...pageProps} />
    </>
  );
}

// export default MyApp;