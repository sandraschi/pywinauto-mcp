import path from "node:path";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
	plugins: [react()],
	resolve: {
		alias: {
			"@": path.resolve(__dirname, "./src"),
		},
	},
	server: {
		allowedHosts: ["goliath"],
		port: 10788,
		strictPort: true,
		host: "127.0.0.1",
		proxy: {
			"/api": {
				target: "http://127.0.0.1:10789",
				changeOrigin: true,
			},
		},
	},
	preview: {
		port: 10788,
		strictPort: true,
		host: "127.0.0.1",
		proxy: {
			"/api": {
				target: "http://127.0.0.1:10789",
				changeOrigin: true,
			},
		},
	},
});
