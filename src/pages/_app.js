import {NextSeo} from "next-seo";
import {ThemeProvider} from 'styled-components';
import withDarkMode, { useDarkMode } from 'next-dark-mode';
import { lightTheme, darkTheme } from '../themes/default';
import GlobalStyles from "../styles/globals";

function App({ Component, pageProps }) {
  const { darkModeActive } = useDarkMode();
  const theme = darkModeActive ? darkTheme : lightTheme;

  return (
    <>
      <ThemeProvider theme={{darkMode: darkModeActive, ...theme}}>
        <NextSeo
          title="Muhammed Humam Hossain's Portfolio"
          description="The personal website for Muhammed Humam Hossain, Full-Stack developer."
          openGraph={{
            type: 'website',
            locale: 'en_GB',
            url: '',
            description: 'The personal website for Muhammed Humam Hossain, Full-Stack developer.',
            site_name: 'Muhammed Humam Hossain | https://humam-hossain.vercel.app/',
          }}
        />
        <GlobalStyles />
        <Component {...pageProps} />
      </ThemeProvider>
    </>
  );
}

export default withDarkMode(App);