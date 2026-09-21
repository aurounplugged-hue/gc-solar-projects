const json = (body, status = 200) => new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json', 'access-control-allow-origin': '*' } });

export async function onRequestOptions() {
  return new Response(null, { status: 204, headers: { 'access-control-allow-origin': '*', 'access-control-allow-methods': 'POST, OPTIONS', 'access-control-allow-headers': 'Content-Type' } });
}

export async function onRequestPost({ request, env }) {
  let data;
  try { data = await request.json(); } catch { return json({ error: 'Invalid request.' }, 400); }
  const required = ['name', 'organization', 'phone', 'project', 'message'];
  if (required.some((field) => !String(data[field] || '').trim())) return json({ error: 'Please complete all fields.' }, 400);
  if (String(data.website || '').trim()) return json({ ok: true });
  const key = env.WEB3FORMS_ACCESS_KEY;
  if (!key) return json({ error: 'The inquiry service is not configured yet.' }, 503);
  const payload = {
    access_key: key,
    subject: `GC Solar inquiry from ${String(data.name).trim()}`,
    from_name: 'GC Solar Projects website',
    name: String(data.name).trim(),
    organization: String(data.organization).trim(),
    phone: String(data.phone).trim(),
    project: String(data.project).trim(),
    message: String(data.message).trim(),
    replyto: String(data.phone).trim()
  };
  const response = await fetch('https://api.web3forms.com/submit', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(payload) });
  if (!response.ok) return json({ error: 'Unable to submit the inquiry right now.' }, 502);
  return json({ ok: true });
}
