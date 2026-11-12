import http from 'node:http';
import { createReadStream } from 'node:fs';
import { stat } from 'node:fs/promises';
import { extname, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(fileURLToPath(new URL('..', import.meta.url)));
const mime = {
  '.html':'text/html; charset=utf-8', '.js':'text/javascript; charset=utf-8',
  '.json':'application/json; charset=utf-8', '.css':'text/css; charset=utf-8',
  '.woff2':'font/woff2', '.mp3':'audio/mpeg', '.m4a':'audio/mp4',
  '.mp4':'video/mp4', '.png':'image/png', '.svg':'image/svg+xml',
};

export function createServer() {
  return http.createServer(async (req,res) => {
    try {
      if (req.method !== 'GET' && req.method !== 'HEAD') {
        res.writeHead(405); res.end(); return;
      }
      const pathname = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
      const filename = resolve(root, '.'+pathname, pathname.endsWith('/') ? 'index.html' : '.');
      if (filename !== root && !filename.startsWith(root+sep)) {
        res.writeHead(403); res.end(); return;
      }
      const info=await stat(filename);
      if (!info.isFile()) { res.writeHead(404); res.end(); return; }
      const headers={ 'Content-Type':mime[extname(filename)] || 'application/octet-stream',
        'Accept-Ranges':'bytes', 'Cache-Control':'no-store' };
      let start=0, end=info.size-1, status=200;
      const range=req.headers.range?.match(/^bytes=(\d*)-(\d*)$/);
      if (range) {
        start=range[1] ? Number(range[1]) : 0;
        end=range[2] ? Math.min(Number(range[2]), info.size-1) : info.size-1;
        if (start>end || start>=info.size) {
          res.writeHead(416,{'Content-Range':`bytes */${info.size}`}); res.end(); return;
        }
        status=206; headers['Content-Range']=`bytes ${start}-${end}/${info.size}`;
      }
      headers['Content-Length']=end-start+1;
      res.writeHead(status,headers);
      if (req.method==='HEAD') { res.end(); return; }
      createReadStream(filename,{start,end}).on('error',()=>res.destroy()).pipe(res);
    } catch (error) {
      res.writeHead(error.code==='ENOENT'?404:500);
      res.end(error.code==='ENOENT'?'Not found':'Server error');
    }
  });
}

if (process.argv[1] && resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
  const port=Number(process.env.PORT || 4173);
  createServer().listen(port,'0.0.0.0',()=>console.log(`Polio animation ready on http://0.0.0.0:${port}`));
}
