/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable React strict mode for better development experience
  reactStrictMode: true,
  
  // Transpile the shared-types package
  transpilePackages: ['@mcleuker/shared-types'],
};

export default nextConfig;
