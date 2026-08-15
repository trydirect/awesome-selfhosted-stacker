Deno.serve(async (req) => {
  const { name } = await req.json();
  const data = {
    message: `Hello ${name || "World"}!`,
  };
  return new Response(JSON.stringify(data), {
    headers: { "Content-Type": "application/json", "Connection": "keep-alive" },
  });
});
