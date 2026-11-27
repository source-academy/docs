import { defineConfig } from "vitepress";

export default defineConfig({
  title: "Source Academy Documentation",
  description: "Documentation for Source Academy",

  lang: "en-US",
  cleanUrls: true,
  srcDir: "app",
  outDir: "dist",

  // The BibTeX file in app/public is a download, not a page: the link checker does not know the extension.
  ignoreDeadLinks: [/^\/source-academy\.bib$/],

  head: [
    [
      "link",
      { rel: "icon", type: "image/x-icon", href: "/img/sourcepower.ico" },
    ],
  ],

  themeConfig: {
    logo: "/img/sourcepower.ico",
    siteTitle: "Source Academy Documentation",

    nav: [
      { text: "Docs", link: "/docs/intro" },
      { text: "Assessment Guide", link: "/docs/assessment/README" },
      { text: "About", link: "/about" },
      {
        text: "GitHub",
        link: "https://github.com/source-academy",
      },
    ],

    sidebar: [
      {
        text: "Getting Started",
        items: [{ text: "Start Here", link: "/docs/intro" }],
      },
      {
        text: "Assessment Guide",
        items: [
          { text: "Assessment Configuration", link: "/docs/assessment/README" },
        ],
      },
      {
        text: "Developers",
        items: [
          {
            text: "Writing a visualizer plugin",
            link: "/docs/developers/writing-a-visualizer-plugin",
          },
          { text: "Node.js version", link: "/docs/developers/node-version" },
        ],
      },
      {
        text: "Contributing",
        items: [
          {
            text: "Cleaning up comments",
            link: "/docs/contributing/comment-cleanup",
          },
        ],
      },
      {
        text: "Publications",
        items: [{ text: "Publications", link: "/docs/publications/" }],
      },
    ],

    footer: {
      message: "Built with VitePress.",
      copyright: `Copyright © ${new Date().getFullYear()} Source Academy.`,
    },

    socialLinks: [
      { icon: "github", link: "https://github.com/source-academy" },
    ],

    search: {
      provider: "local",
    },
  },
});
