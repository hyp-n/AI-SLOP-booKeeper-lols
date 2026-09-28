import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// GitHub Pages: set base to '/<repo-name>/' when deploying
// Repo name comes from GITHUB_REPOSITORY env var (format: owner/repo)
const isGitHubPages = process.env.GITHUB_PAGES === 'true';
const repoName = process.env.GITHUB_REPOSITORY?.split('/')[1] || 'bookeeper';

export default defineConfig({
  plugins: [react()],
  base: isGitHubPages ? `/${repoName}/` : '/',
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:5000",
        changeOrigin: true,
      },
    },
  },
});
