import { defineConfig } from "vitepress";

export default defineConfig({
  title: "Source Academy Documentation",
  description: "Documentation for Source Academy",

  lang: "en-US",
  // Published at the root of https://docs.sourceacademy.org, in the folders developer, educator and learner (see
  // .github/workflows/deploy.yml). The root page belongs to js-slang (a redirect to /javascript), and the root folders
  // to the other publishers: this site has no root page, and keeps its own files under docs-assets.
  base: "/",
  assetsDir: "docs-assets",
  cleanUrls: true,
  srcDir: "app",
  outDir: "dist",

  head: [
    [
      "link",
      {
        rel: "icon",
        type: "image/x-icon",
        href: "/docs-assets/img/sourcepower.ico",
      },
    ],
  ],

  themeConfig: {
    logo: "/docs-assets/img/sourcepower.ico",
    siteTitle: "Source Academy Documentation",

    nav: [
      { text: "Developer", link: "/developer/" },
      { text: "Educator", link: "/educator/" },
      { text: "Learner", link: "/learner/" },
      { text: "About", link: "https://about.sourceacademy.org/" },
      {
        text: "GitHub",
        link: "https://github.com/source-academy",
      },
    ],

    sidebar: {
      "/developer/": [
        {
          text: "Developers",
          items: [
            {
              text: "Writing a visualizer plugin",
              link: "/developer/writing-a-visualizer-plugin",
            },
            { text: "Node.js version", link: "/developer/node-version" },
            {
              text: "Cleaning up comments",
              link: "/developer/comment-cleanup",
            },
          ],
        },
      ],
      "/educator/": [
        {
          text: "Educators",
          items: [
            { text: "Assessment configuration", link: "/educator/assessment/" },
          ],
        },
      ],
      "/learner/": [
        {
          text: "Learners",
          items: [
            { text: "Versions and names", link: "/learner/versions-and-names" },
          ],
        },
      ],
    },

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
