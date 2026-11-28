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
    // The site has no root page (the root belongs to js-slang's redirect), so the logo goes to the front door.
    logoLink: "https://about.sourceacademy.org/",
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
        {
          text: "Architecture",
          items: [
            { text: "Overview", link: "/developer/architecture/" },
            { text: "Frontend", link: "/developer/architecture/frontend" },
            { text: "Backend", link: "/developer/architecture/backend" },
            { text: "Grader", link: "/developer/architecture/grader" },
            {
              text: "Directories",
              link: "/developer/architecture/directories",
            },
            { text: "Conductor", link: "/developer/architecture/conductor" },
            { text: "Evaluators", link: "/developer/architecture/evaluators" },
            {
              text: "Plugins and modules",
              link: "/developer/architecture/plugins-and-modules",
            },
            { text: "Deployment", link: "/developer/architecture/deployment" },
            {
              text: "A run and a submission",
              link: "/developer/architecture/run-and-submission",
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
