# Lead time e análise de movimentação de stages

Quando o Lucas pede "quanto tempo médio entre Stage 3 e Stage 99?", "lead time de fechamento", "quanto tempo cada deal fica em cada stage".

## Campos relevantes

Cada stage tem um campo de data correspondente que registra **quando** o deal entrou naquele stage. Padrão observado:

- `apwip_stage1` — data de entrada em Stage 1 (Identification)
- `apwip_stage3` — data de entrada em Stage 3 (mais comum como ponto de início da análise)
- `apwip_stage99closedandfundeddeal` — data de Stage 99 (deal fechado e fundado)

Os nomes exatos variam por versão da customização da APW. Se o nome aqui não funcionar, ver `troubleshooting.md` — tem snippet de descoberta de campos.

## Snippet base: lead time Stage 3 → Stage 99

```js
(async () => {
  const fetchXml = `<fetch version='1.0' mapping='logical'>
    <entity name='opportunity'>
      <attribute name='opportunityid'/>
      <attribute name='apwip_autonumberid'/>
      <attribute name='apwip_stage3'/>
      <attribute name='apwip_stage99closedandfundeddeal'/>
      <attribute name='_ownerid_value'/>
      <filter type='and'>
        <condition attribute='apwip_stage99closedandfundeddeal' operator='not-null'/>
        <condition attribute='apwip_stage3' operator='not-null'/>
      </filter>
    </entity>
  </fetch>`;
  const r = await fetch(`${window.location.origin}/api/data/v9.2/opportunities?fetchXml=${encodeURIComponent(fetchXml)}`, {
    headers: {'Accept':'application/json','OData-MaxVersion':'4.0','OData-Version':'4.0','Prefer':'odata.include-annotations=*'}
  });
  const d = await r.json();
  // Calcula lead time em dias por deal
  const leadtimes = d.value.map(o => {
    const s3 = new Date(o.apwip_stage3);
    const s99 = new Date(o.apwip_stage99closedandfundeddeal);
    const days = Math.round((s99 - s3) / (1000 * 60 * 60 * 24));
    return {lnum: o.apwip_autonumberid, days, s3, s99};
  });
  // Estatísticas
  const sorted = [...leadtimes].sort((a,b) => a.days - b.days);
  const sum = leadtimes.reduce((s, x) => s + x.days, 0);
  return {
    count: leadtimes.length,
    mean: Math.round(sum / leadtimes.length),
    median: sorted[Math.floor(sorted.length/2)].days,
    p25: sorted[Math.floor(sorted.length * 0.25)].days,
    p75: sorted[Math.floor(sorted.length * 0.75)].days,
    min: sorted[0].days,
    max: sorted[sorted.length - 1].days,
    samples: leadtimes.slice(0, 5)
  };
})();
```

## Cohort analysis

Se ele pedir "lead time por ano de início" ou "por diretor":

```js
// Após ter `leadtimes` calculados, agrupa:
const byOwner = {};
leadtimes.forEach(lt => {
  const owner = lt.ownerid_value; // adiciona esse campo no map
  if (!byOwner[owner]) byOwner[owner] = [];
  byOwner[owner].push(lt.days);
});
const stats = Object.entries(byOwner).map(([owner, days]) => ({
  owner,
  n: days.length,
  median: days.sort((a,b)=>a-b)[Math.floor(days.length/2)],
  mean: Math.round(days.reduce((s,d)=>s+d,0) / days.length)
}));
```

Para resolver o GUID do owner em nome, faça um segundo fetch:
```js
fetch(`${window.location.origin}/api/data/v9.2/systemusers?$filter=systemuserid in ('GUID_1','GUID_2')&$select=systemuserid,fullname`)
```

## Cuidados na interpretação

1. **Deals em andamento não entram** — filtramos por `stage99 not-null`. Isso vicia pra deals que já fecharam, ou seja, **survivor bias**. Se o Lucas quer projetar quanto tempo deals atuais vão demorar, isso subestima. Comunica isso.

2. **Outliers** — deals que ficam 800+ dias provavelmente foram pausados/reativados. Mostre média **e** mediana. Mediana é mais honesta pra esse tipo de pergunta.

3. **Mudança de processo** — a APW pode ter mudado fluxo de stages no passado. Deals antigos podem ter lead time não comparável a deals novos. Se o Lucas suspeitar disso, segmenta por ano de Stage 3.

4. **Stage skipping** — alguns deals pulam stages. Confere `apwip_stage1`, `apwip_stage2` etc também — se algum estiver null no meio, registra como anomalia mas não exclui da análise sem perguntar.

## Apresentação

Dump pro Lucas no formato:
```
Lead time Stage 3 → Stage 99 (N=297 deals fechados):
  Mediana: 87 dias
  Média: 124 dias (puxada por outliers)
  P25-P75: 52-152 dias
  Min/Max: 14 / 892 dias
```

Se ele quiser ver os outliers, mostra os top 5 e bottom 5 (códigos L apenas, não detalhes).
