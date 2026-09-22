# Verified binary image upload workflow

This workflow is required for uploading JPEG images to `gc-solar-projects`. It prevents binary data from being converted into UTF-8 text and silently corrupted.

## Why ordinary text handling corrupts images

JPEGs are arbitrary bytes, not UTF-8 text. If a binary file is read, printed, or passed through a text-oriented buffer, invalid UTF-8 sequences can be replaced with the Unicode replacement character U+FFFD. Its UTF-8 bytes are `EF BF BD`; in base64 this appears as `77+9`.

A corrupted JPEG can therefore look like a text file while retaining a `.jpeg` extension. Do not judge binary bytes from sandbox stdout: stdout can itself display mangled replacement artifacts. Inspect files through byte counts, ASCII base64, and API responses instead.

## 1. Create a dedicated branch

Never push directly to `master`.

```sh
git checkout master
git pull origin master
git checkout -b docs-or-fix-branch-name
```

For GitHub API workflows, create the branch from the current `master` commit and use that branch for every upload. Always open a PR targeting `master`.

## 2. Retrieve the clean binary directly to disk

For a short-lived media URL, generate a fresh signed URL immediately before downloading. Do not reuse an expired URL.

```sh
rm -f /tmp/image.jpeg
curl --fail -sS -L "<fresh-signed-url>" -o /tmp/image.jpeg
wc -c /tmp/image.jpeg
```

`--fail` is important: it prevents an HTTP error page from being saved as the image. Confirm the command succeeds and record the exact byte count.

## 3. Create an ASCII base64 file

Use the shell encoder to read the binary and write only ASCII base64 to a file:

```sh
base64 -w 0 /tmp/image.jpeg > /tmp/image_b64.txt
head -c 20 /tmp/image_b64.txt
```

For a clean JPEG, the base64 must start with `/9j/`, representing the JPEG SOI bytes beginning `FF D8 FF` (normally `FF D8 FF E0` for a JFIF image). The ending should represent the JPEG EOI bytes `FF D9`; common base64 endings include `9k=`. Verify that the base64 contains no replacement signature:

```sh
case "$(head -c 4 /tmp/image_b64.txt)" in /9j/) echo "clean JPEG header";; *) echo "ERROR: not a clean JPEG"; exit 1;; esac
! grep -q '77+9' /tmp/image_b64.txt
tail -c 8 /tmp/image_b64.txt
```

Never echo raw binary bytes to stdout. Never concatenate raw base64 into JSON with shell `printf` or `cat`; line wrapping, quoting, and stdout conversion can corrupt the request.

## 4. Upload with GitHub Contents API

Use `js-exec` and `fetch`. Read the already-generated ASCII file as text. Do not read the image as UTF-8 text and do not use `buf.toString('base64')` when the buffer has already passed through a mangling text path.

```js
const fs = require('fs');
const token = fs.readFileSync('.github_token', 'utf8').trim();
const imagePath = '/tmp/image.jpeg';
const b64Path = '/tmp/image_b64.txt';
const content = fs.readFileSync(b64Path, 'utf8').trim();
const sourceBytes = fs.statSync(imagePath).size;
const branch = 'docs-or-fix-branch-name';
const api = 'https://api.github.com/repos/aurounplugged-hue/gc-solar-projects/contents/images/projects/image.jpeg';

// Get the current blob SHA for an update.
const currentResponse = await fetch(`${api}?ref=${branch}`, {
  headers: {
    Authorization: `Bearer ${token}`,
    'User-Agent': 'gc-solar-projects-binary-upload',
    Accept: 'application/vnd.github.v3+json'
  }
});
const current = await currentResponse.json();
if (!currentResponse.ok) throw new Error(JSON.stringify(current));

const response = await fetch(api, {
  method: 'PUT',
  headers: {
    Authorization: `Bearer ${token}`,
    'User-Agent': 'gc-solar-projects-binary-upload',
    Accept: 'application/vnd.github.v3+json',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    message: 'fix: restore clean binary for image.jpeg',
    content,
    branch,
    sha: current.sha
  })
});
const result = await response.json();
if (!response.ok) throw new Error(JSON.stringify(result));
if (result.content.size !== sourceBytes) {
  throw new Error(`size mismatch: source=${sourceBytes}, GitHub=${result.content.size}`);
}
console.log(JSON.stringify({sourceBytes, githubSize: result.content.size, blobSha: result.content.sha}));
```

Run it with:

```sh
js-exec upload-image.js
```

The API response must report a GitHub blob size equal to the original `wc -c` result. Save the returned blob SHA.

## 5. Verify the resulting GitHub blob

Fetch the file from the branch through the GitHub Contents API and inspect the returned base64 without decoding it through stdout:

```js
const response = await fetch(`${api}?ref=${branch}`, { headers });
const file = await response.json();
const githubBase64 = file.content.replace(/\n/g, '');
if (file.size !== sourceBytes) throw new Error('GitHub byte count mismatch');
if (!githubBase64.startsWith('/9j/')) throw new Error('GitHub blob is not a JPEG');
if (githubBase64.includes('77+9')) throw new Error('replacement-byte signature found');
console.log({size: file.size, sha: file.sha, header: githubBase64.slice(0, 20)});
```

The post-upload checks must confirm:

- GitHub size equals the source byte count.
- The returned SHA is recorded.
- Base64 starts with `/9j/`.
- There are zero occurrences of `77+9`.
- The decoded binary has JPEG SOI `FF D8 FF` and EOI `FF D9` when checked with a byte-safe file tool, not mangled stdout.

## 6. Repository and PR checks

Before presenting the PR:

```sh
wc -c path/to/every-changed-file
 git diff --stat
```

For image-only changes, the diff is a binary-file change with no meaningful text additions or deletions. For any changed HTML, CSS, Markdown, or configuration file, also verify valid UTF-8 and zero NUL bytes. For HTML files, verify the expected `<!doctype html>` through `</html>` tags. Validate `_headers` syntax when `_headers` is changed.

The PR must include:

- Exact byte count for every changed file.
- Exact `git diff --stat` output, including additions and deletions.
- Binary verification results for each JPEG.
- CI/check status.
- Cloudflare Pages or deploy-preview URL, if provided by the deployment checks.

## 7. Approval and merge policy

Open a pull request from the dedicated branch to `master`. Never merge automatically. ipoG must give explicit approval after reviewing the PR, byte counts, diff, checks, and preview. Only then merge the PR through GitHub API, and verify the resulting `master` commit SHA and branch status.
