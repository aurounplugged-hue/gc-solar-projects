const RECIPIENT = 'chidvilas@gcsolarprojects.com';
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

  const fields = {
    _subject: `GC Solar inquiry from ${String(data.name).trim()}`,
    _captcha: 'false',
    name: String(data.name).trim(),
    organization: String(data.organization).trim(),
    phone: String(data.phone).trim(),
    project: String(data.project).trim(),
    message: String(data.message).trim()
  };

  // FormSubmit requires no API key or dashboard. The first submission triggers a
  // one-time confirmation email to the recipient; subsequent leads are delivered directly.
  const response = await fetch(`https://formsubmit.co/ajax/${encodeURIComponent(RECIPIENT)}`, {
    method: 'POST',
    headers: { 'content-type': 'application/json', accept: 'application/json' },
    body: JSON.stringify(fields)
  });
  if (!response.ok) return json({ error: 'Unable to submit the inquiry right now.' }, 502);
  const result = await response.json().catch(() => ({}));
  if (result.success === false) return json({ error: 'The inquiry service rejected the submission.' }, 502);
  return json({ ok: true });
}
