/* dump-slices.js — devolve UMA fatia do raw.json guardado por collection.js.
   Rode depois do collection.js. Ajuste I a cada chamada: 0, 1, 2, ... até n_slices-1.
   O Claude concatena todas as fatias na ordem e faz JSON.parse -> salva como raw.json.

   Fluxo: collection.js devolveu { n_slices: N, slice_size: S }.
   Para i de 0 a N-1, rode este snippet com I = i; cole o retorno em ordem; remonte. */
(() => {
  const I = 0;            // <<< MUDE este índice a cada chamada (0,1,2,...)
  const S = 500000;       // deve bater com SLICE do collection.js
  const str = window.__APW_AUDIT_STR;
  if (!str) return JSON.stringify({ error: "window.__APW_AUDIT_STR vazio. Rode collection.js antes." });
  const start = I * S, end = Math.min(str.length, start + S);
  return JSON.stringify({ i: I, start, end, total: str.length, last: end >= str.length, chunk: str.slice(start, end) });
})();
