// ═══════════════════════════════════════════════════════════════
// APW · OPCIONAL · scrape da autoavaliação no UKG/UltiPro
// Rodar com a página da avaliação ABERTA (Resumo da Avaliação do diretor)
// Captura os 7 blocos de meta + nota + comentário
// Baixa JSON pra alimentar o build_review.py sem copy/paste manual
// ═══════════════════════════════════════════════════════════════
(async () => {
  // UKG renderiza as metas em divs; o seletor pode variar por versão
  // Tenta 3 estratégias e cai pra fallback de prompt
  const seletores = [
    'div[data-automation-id="goal-item"]',
    '.goal-item',
    '.evaluation-section'
  ];

  let items = [];
  for (const sel of seletores) {
    const nodes = document.querySelectorAll(sel);
    if (nodes.length > 0) {
      console.log(`✓ Seletor que funcionou: ${sel} (${nodes.length} nodes)`);
      items = Array.from(nodes).map((n, i) => ({
        idx: i + 1,
        titulo: (n.querySelector('h3,h4,.goal-title')?.innerText || '').trim(),
        peso: (n.querySelector('.weight,[data-automation-id="weight"]')?.innerText || '').trim(),
        nota_funcionario: (n.querySelector('.self-rating,[data-automation-id="rating"]')?.innerText || '').trim(),
        comentario: (n.querySelector('.comment,textarea,[data-automation-id="comment"]')?.innerText || '').trim(),
        html_raw: n.innerHTML.substring(0, 500)
      }));
      break;
    }
  }

  if (items.length === 0) {
    console.warn('⚠ Nenhum seletor conhecido funcionou. UKG mudou o layout?');
    console.warn('  Inspecione um bloco de meta no DevTools e me passe o seletor.');
    console.warn('  Fallback: copie manualmente o texto pra inputs/<diretor>/autoavaliacao.md');
    return;
  }

  // nome do diretor + ciclo (header da página)
  const nome = (document.querySelector('h1, [data-automation-id="employee-name"]')?.innerText || 'desconhecido').trim();
  const ciclo = (document.querySelector('[data-automation-id="review-cycle"], .cycle-title')?.innerText || '').trim();

  const out = { diretor: nome, ciclo: ciclo, scraped_at: new Date().toISOString(), metas: items };
  console.log(JSON.stringify(out, null, 2));

  const slug = nome.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/[^a-z]+/g,'-').replace(/^-|-$/g,'');
  const blob = new Blob([JSON.stringify(out, null, 2)], {type:'application/json'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `autoavaliacao_${slug}_${new Date().toISOString().substring(0,10)}.json`;
  a.click();
  console.log(`\n✓ ${a.download}`);
})();
