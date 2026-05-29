export async function onRequest(context) {
  const incoming = context.request;
  const url = new URL(incoming.url);
  const apiUrl = new URL('https://api.soda567.dpdns.org/api/' + (context.params.path || ''));
  apiUrl.search = url.search;

  const headers = new Headers(incoming.headers);
  headers.set('host', apiUrl.host);
  headers.delete('cf-connecting-ip');
  headers.delete('cf-ipcountry');
  headers.delete('cf-ray');
  headers.delete('cf-visitor');
  headers.delete('x-forwarded-proto');
  headers.delete('x-real-ip');

  const init = {
    method: incoming.method,
    headers,
    redirect: 'manual'
  };
  if (!['GET', 'HEAD'].includes(incoming.method)) {
    init.body = incoming.body;
  }

  if (incoming.method === 'OPTIONS') {
    return new Response(null, {
      status: 204,
      headers: {
        'access-control-allow-origin': url.origin,
        'access-control-allow-methods': 'GET,POST,OPTIONS,DELETE,PATCH',
        'access-control-allow-headers': 'Content-Type,Authorization,X-Soda-Access-Token,X-Request-ID'
      }
    });
  }

  const response = await fetch(apiUrl.toString(), init);
  const outHeaders = new Headers(response.headers);
  outHeaders.delete('content-security-policy');
  outHeaders.delete('content-encoding');
  outHeaders.set('access-control-allow-origin', url.origin);
  outHeaders.set('access-control-allow-methods', 'GET,POST,OPTIONS,DELETE,PATCH');
  outHeaders.set('access-control-allow-headers', 'Content-Type,Authorization,X-Soda-Access-Token,X-Request-ID');
  return new Response(response.body, { status: response.status, statusText: response.statusText, headers: outHeaders });
}
