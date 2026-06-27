/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone', // <--- THIS IS THE FIX
  typescript: {
    ignoreBuildErrors: true,
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
}

module.exports = nextConfig