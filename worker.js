export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    if (url.pathname === "/api/health") {
      return new Response(JSON.stringify({ status: "online", system: "SaudiAqarAI Engine 2.0" }), {
        headers: { "content-type": "application/json;charset=UTF-8" },
      });
    }

    return env.ASSETS.fetch(request);
  },
};
