// @ts-check

const lightCodeTheme = require('prism-react-renderer').themes.github;
const darkCodeTheme = require('prism-react-renderer').themes.dracula;

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Light OLT',
  tagline: 'Customize the behavior, keep the platform stable',
  favicon: 'img/favicon.svg',

  url: 'https://abelperezr.github.io',
  baseUrl: '/olt-light/',
  organizationName: 'abelperezr',
  projectName: 'olt-light',
  trailingSlash: false,
  onBrokenLinks: 'throw',
  markdown: {
    hooks: {onBrokenMarkdownLinks: 'warn'},
  },

  i18n: {
    defaultLocale: 'es',
    locales: ['es', 'en'],
    localeConfigs: {
      es: {label: 'Español', htmlLang: 'es'},
      en: {label: 'English', htmlLang: 'en'},
    },
  },

  presets: [
    [
      'classic',
      {
        docs: {
          routeBasePath: 'docs',
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl: 'https://github.com/abelperezr/olt-light/edit/main/website/',
          showLastUpdateTime: true,
        },
        blog: false,
        theme: {customCss: require.resolve('./src/css/custom.css')},
      },
    ],
  ],

  themeConfig: {
    image: 'img/social-card.svg',
    colorMode: {
      defaultMode: 'dark',
      disableSwitch: false,
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: 'Light OLT',
      logo: {alt: 'Light OLT', src: 'img/logo.svg'},
      items: [
        {to: '/docs/', label: 'Docs', position: 'left'},
        {type: 'localeDropdown', position: 'right'},
        {
          href: 'https://github.com/abelperezr/olt-light',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Documentation',
          items: [
            {label: 'Tutorials', to: '/docs/tutorials/first-build'},
            {label: 'How-to', to: '/docs/how-to/customize-ecli'},
            {label: 'Reference', to: '/docs/reference/project-layout'},
            {label: 'Explanation', to: '/docs/explanation/architecture'},
          ],
        },
        {
          title: 'Project',
          items: [
            {label: 'GitHub', href: 'https://github.com/abelperezr/olt-light'},
            {label: 'Container images', href: 'https://github.com/abelperezr?tab=packages'},
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Abel Perez and Eluzmar Alviarez · Built with Docusaurus`,
    },
    prism: {theme: lightCodeTheme, darkTheme: darkCodeTheme},
  },
};

module.exports = config;
