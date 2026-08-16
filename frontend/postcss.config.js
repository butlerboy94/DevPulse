// PostCSS pipeline: runs Tailwind to generate utility classes, then
// autoprefixer to add vendor prefixes for older browsers.
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
