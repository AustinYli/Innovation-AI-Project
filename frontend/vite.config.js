const railwayHost = process.env.RAILWAY_PUBLIC_DOMAIN;

export default {
  server: {
    host: "0.0.0.0",
    allowedHosts: [
      "frontend-production-71e0.up.railway.app",
      railwayHost,
    ].filter(Boolean),
  },
};
